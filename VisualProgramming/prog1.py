data = [['hong20230101', 90,70], 
    ['kang20230202', 88,95], 
    ['lee20220303', 85,80], 
    ['so20210505', 40,45]]

test_data = []
for entry in data:
    id_name = entry[0]
    total_score = entry[1] + entry[2]
    test_data.append([id_name[-8:], id_name[:-8], total_score])

# Sort하기. 오름차순으로하기
sorted_data = sorted(test_data, key=lambda x: x[2], reverse=True)

print(f"{'rank':<5}{'id':<10}{'name':<8}{'total':<5}")

for rank, entry in enumerate(sorted_data, start=1):
    print(f"{rank:<5}{entry[0]:<10}{entry[1]:<8}{entry[2]:<5}")
