def check_data():
    print('"=" * 4    print("       CHUONG TRINH KIEM TRA DU LIEU")')
    
    print("=" * 45)

    print("Nhap du lieu cua ban.")
    print("Phan cach cac gia tri bang dau phay (,)")
    print("Vi du: 10, 20, abc, 30, 40")
    print("Nhap END o mot dong rieng de ket thuc.")

    lines = []

    while True:
        line = input()

        if line.strip().upper() == "END":
            break

        lines.append(line)

    
    raw_data = "\n".join(lines)

    
    items = raw_data.replace("\n", ",").split(",")

    valid_numbers = []
    invalid_data = []

    
    for item in items:
        item = item.strip()

        
        if item == "":
            continue

        try:
            number = float(item)
            valid_numbers.append(number)
        except ValueError:
            invalid_data.append(item)

    
    print("\n" + "=" * 45)
    print("KET QUA KIEM TRA")
    print("=" * 45)

    print("Tong so gia tri hop le:", len(valid_numbers))
    print("Tong so gia tri loi:", len(invalid_data))

    if invalid_data:
        print("\nDu lieu khong hop le:")
        for value in invalid_data:
            print("-", value)
    else:
        print("\nKhong phat hien du lieu loi.")

    if valid_numbers:
        total = sum(valid_numbers)
        average = total / len(valid_numbers)

        print("\nTHONG KE DU LIEU")
        print("-" * 30)
        print("Tong:", total)
        print("Trung binh:", round(average, 2))
        print("Gia tri lon nhat:", max(valid_numbers))
        print("Gia tri nho nhat:", min(valid_numbers))
    else:
        print("\nKhong co so hop le de thong ke.")

    print("\nHoan thanh kiem tra!")

check_data()

