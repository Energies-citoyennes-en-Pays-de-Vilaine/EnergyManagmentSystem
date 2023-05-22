from typing import List


def persistance_prediction(curve) -> List[int]:
	to_return_data = []
	current_data = curve[-1]
	old_data = curve[0]
	len_curve = len(curve)

	for i in range(len_curve):
		current_data += curve[i] - old_data
		old_data = curve[i]
		to_add_data = current_data * (len_curve - i) / len_curve + curve[i] * i / len_curve
		current_data = to_add_data
		to_return_data.append(to_add_data)
	return to_return_data