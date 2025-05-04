import subprocess

def extend_key_expiration(fingerprint, new_expire="1y"):
    cmd = f"gpg --batch --yes --pinentry-mode loopback --passphrase 'your_passphrase' --quick-set-expire {fingerprint} {new_expire}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Key {fingerprint} expiration extended to {new_expire}")
    else:
        print("Error:", result.stderr)

# ตัวอย่างการใช้งาน
fingerprint = "A253AA0A9E719B4A142903B3F31FE952F292C399"
extend_key_expiration(fingerprint, "2y")  # ต่ออายุ 2 ปี










