import matplotlib.pyplot as plt

# Load grade values from the file
file_path = 'data/id_6929029131_road_grade.txt'
grades = []

with open(file_path, 'r') as file:
    for line in file:
        try:
            grade = float(line.strip())
            grades.append(grade)
        except ValueError:
            pass  # Ignore lines that are not valid floats

# Generate x-axis values (assuming each grade represents an equal segment of the road)
x_values = range(1, len(grades) + 1)

# Plot the road grade profile
plt.figure(figsize=(10, 6))
plt.plot(x_values, grades, color='blue', linewidth=2, label='Road Grade (%)')
plt.fill_between(x_values, grades, color='skyblue', alpha=0.3)

# Annotate the plot
plt.title('Road Grade Profile')
plt.xlabel('Segment Index')
plt.ylabel('Grade (%)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.axhline(0, color='black', linewidth=0.8)  # Reference line at 0%
plt.legend()

plt.tight_layout()
plt.show()
