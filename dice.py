import random
class Dice:
    def validate_probabilities(probabilities):
        if not isinstance(probabilities, list):
            return False, "probabilities must be a list."
    
        if len(probabilities) != 6:
            return False, f"probabilities must contain exactly 6 values, got {len(probabilities)}."
    
        for i, p in enumerate(probabilities):
            if not isinstance(p, (int, float)):
                return False, f"All probabilities must be numeric. Got '{type(p).__name__}' at index {i}."
            if p < 0:
                return False, f"All probabilities must be non-negative. Got {p} at index {i}."
    
        total = sum(probabilities)
        if not abs(total - 1.0) < 1e-9:
            return False, f"probabilities must sum to 1.0, but got {total:.10f}."
    
        return True, ""
    
    
    def roll_biased_dice(probabilities, number_of_random):
        # Build cumulative distribution
        cumulative = []
        running_sum = 0.0
        for p in probabilities:
            running_sum += p
            cumulative.append(running_sum)
    
        results = []
        for _ in range(number_of_random):
            r = random.random()
            for face_index, threshold in enumerate(cumulative):
                if r < threshold:
                    results.append(face_index + 1)
                    break
            else:
                results.append(6)  # edge case: r == 1.0
    
        return results
