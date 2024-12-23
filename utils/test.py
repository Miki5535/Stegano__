import ctypes

# ระบุไฟล์ DLL โดยใช้ path ที่ถูกต้อง
example = ctypes.CDLL(r"C:\Users\65011\Desktop\Segano\work00002\example.dll")


# ระบุ argument และ return types
example.add.argtypes = [ctypes.c_int, ctypes.c_int]
example.add.restype = ctypes.c_int

# เรียกใช้ฟังก์ชัน
result = example.add(10, 20)
print(f"Result from C: {result}")
