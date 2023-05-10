#!/bin/bash

CONFIG_FILENAME="EMS_systemd_config.txt"
CONFIG_FOLDER="/etc/ems"
HAS_TO_INSTALL_ANACONDA=0
HAS_TO_UPDATE=0
HAS_TO_INSTALL_POSTGRES=0
HAS_TO_CREATE_DATABASE=0
HAS_TO_INSTALL_MILP=0
HAS_TO_CREATE_SERVICES=1
EMS_DB="test"
EMS_USER="testu"
EMS_DB_CONFIG_FILENAME="db_credentials_test.py"

ELFE_OUT_PASS="pass"
ELFE_OUT_USER="testeu"
ELFE_OUT_HOST="localhost"
ELFE_OUT_DB="ems_sortie"

ELFE_DB="elfe_coordo"
ELFE_OPTIONS="-c search_path=test,public"

EMSFOLDER="$(echo $PWD)"
BASHRCPATH="$(echo $HOME)/.bashrc"
if [ "$EUID" -ne 0 ]
	then echo "please run installer as root"
	exit -1
fi

if [ "$HAS_TO_UPDATE" -ne 0 ]
	then
	echo "running apt update and upgrade for you"
	apt update
	apt upgrade -y
	apt autoremove -y
fi
echo "installing the environnement"

if [ "$HAS_TO_INSTALL_ANACONDA" -ne 0 ]
	then
	echo "installing the necessary packets for anaconda"
	apt-get install -y libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
	echo "downloading anaconda installation script in /tmp"
	wget "https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh" -O /tmp/anaconda_installer.sh
	chmod +x /tmp/anaconda_installer.sh
	/tmp/anaconda_installer.sh -b
	eval "$(~/anaconda3/bin/conda shell.bash hook)"
	conda init
	rm /tmp/anaconda_installer.sh
fi

if [ "$HAS_TO_INSTALL_MILP" -ne 0 ] || [ "$HAS_TO_INSTALL_ANACONDA" -ne 0 ]
	then
	echo "installing milp environnement"
	echo "sourcing $BASHRCPATH"
	source "$BASHRCPATH"
	conda env create -f "$EMSFOLDER/anaconda.yml"
fi

echo "activating milp env"
source "$BASHRCPATH"
conda activate milp

if [ "$HAS_TO_INSTALL_POSTGRES" -ne 0 ]
	then
	echo "installing postgresql"
	apt install postgresql
fi

if [ "$HAS_TO_INSTALL_POSTGRES" -ne 0 ] || [ "$HAS_TO_CREATE_DATABASE" -ne 0 ]
	then
	#cleanup
	echo "creating database"
	su - postgres -c "psql -c \"DROP DATABASE $EMS_DB;\""
	su - postgres -c "psql -c \"DROP USER $EMS_USER;\""

	POSTGRES_PASSWORD="$(LC_ALL=C tr -dc '[:alnum:]' < /dev/urandom | head -c20)"
	echo "setting encryption method for password as postgres-s default is really bad"
	su - postgres -c "psql -c \"SET password_encryption  = 'scram-sha-256';\"" >/dev/null
	echo "creating user for EMS ($EMS_USER)"
	su - postgres -c "psql -c \"CREATE USER $EMS_USER WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';\"">/dev/null
	echo "creating database for EMS ($EMS_DB)"
	su - postgres -c "psql -c \"CREATE DATABASE $EMS_DB WITH OWNER $EMS_USER;\"">/dev/null
	echo "copying the db_config file to ($EMS_DB_CONFIG_FILENAME) to populate it with the EMS password"
	cp "$EMSFOLDER/credentials/db_credentials_example.py" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	echo "setting up EMS config for EMS inner database"
	sed -i "s/myEMSSuperHost/localhost/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myEMSSuperDatabase/$EMS_DB/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myEMSSuperUser/$EMS_USER/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myEMSSuperPassword/$POSTGRES_PASSWORD/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"

	echo "setting up EMS config for EMS output database"
	sed -i "s/myOutSuperHost/$ELFE_OUT_HOST/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myOutSuperDatabase/$ELFE_OUT_DB/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myOutSuperUser/$ELFE_OUT_USER/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myOutSuperPassword/$ELFE_OUT_PASS/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"

	echo "setting up EMS config for ELFE database"
	sed -i "s/myELFESuperHost/$ELFE_OUT_HOST/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myELFESuperDatabase/$ELFE_DB/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myELFESuperUser/$ELFE_OUT_USER/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myELFESuperPassword/$ELFE_OUT_PASS/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"
	sed -i "s/myELFESuperOptions/$ELFE_OPTIONS/g" "$EMSFOLDER/credentials/$EMS_DB_CONFIG_FILENAME"

	echo "creating tables for EMS inner database"
	python -m database.EMS_db_creator
	echo "creating tables for EMS output database"
	python -m database.EMS_OUT_db_creator
fi

echo "creating the config folder $CONFIG_FOLDER"
mkdir -p $CONFIG_FOLDER
echo "creating environnement config file for EMS services to launch"
echo "assumes this is where the EMS will live ($EMSFOLDER)"
echo "EMSFOLDER=\"$(echo $EMSFOLDER)\"">$CONFIG_FILENAME
echo "assumes the bashrc file is in there ($BASHRCPATH)"
echo "BASHRCPATH=\"$BASHRCPATH\"">>$CONFIG_FILENAME
echo "moving the config file to its location $CONFIG_FOLDER/$CONFIG_FILENAME"

mv $CONFIG_FILENAME $CONFIG_FOLDER/$CONFIG_FILENAME

if [ "$HAS_TO_CREATE_SERVICES" -ne 0 ]
	then
	echo "copying the services"
	for f in $(ls "$EMSFOLDER/services/systemd_files"); do
		cp "$EMSFOLDER/services/systemd_files/$f" "/etc/systemd/system"
	done
	echo "installing services"
	echo "installing ECS acquisition service"
	systemctl enable ECS_acquisition.timer
	echo "installing EMS launcher service"
	systemctl enable EMS_launcher.timer
	echo "installing learning cleaner service"
	systemctl enable learning_cleaner.timer
	echo "installing machine cycle learner service"
	systemctl enable machine_cycle_learner.timer
	echo "installing power prediction service"
	systemctl enable power_prediction.timer
	echo "installing user temp service"
	systemctl enable user_temp.timer
	echo "installing meteo concept service"
	systemctl enable Meteo_concept.timer
fi