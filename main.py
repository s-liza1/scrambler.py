import cv2
import numpy as np

ROWS = 12
COLS = 16
KEY = 1991

lfsr_state = KEY

def get_next_bit():
    global lfsr_state

    b0 = (lfsr_state >> 0) & 1
    b2 = (lfsr_state >> 2) & 1
    b3 = (lfsr_state >> 3) & 1
    b5 = (lfsr_state >> 5) & 1

    new_bit = b0 ^ b2 ^ b3 ^ b5

    lfsr_state = (lfsr_state >> 1) | (new_bit << 15)
    return new_bit

def get_random_number(max_val):
    number = 0
    for i in range(16):
        bit = get_next_bit()
        number = (number << 1) | bit
    return number % max_val

def make_shuffle_order(total_blocks, seed_key):
    global lfsr_state
    lfsr_state = seed_key

    order = []
    for i in range(total_blocks):
        order.append(i)

    for i in range(total_blocks - 1, 0, -1):
        j = get_random_number(i + 1)
        temp = order[i]
        order[i] = order[j]
        order[j] = temp

    return order

def encrypt_image(img, order):
    h, w, c = img.shape
    bh = h // ROWS
    bw = w // COLS

    blocks = []
    for r in range(ROWS):
        for col in range(COLS):
            piece = img[r * bh : (r + 1) * bh, col * bw : (col + 1) * bw]
            blocks.append(piece)

    scrambled = np.zeros_like(img)

    index = 0
    for r in range(ROWS):
        for col in range(COLS):
            pick_block = order[index]
            scrambled[r * bh : (r + 1) * bh, col * bw : (col + 1) * bw] = blocks[
                pick_block
            ]
            index = index + 1

    return scrambled

def decrypt_image(scrambled_img, order):
    total_blocks = len(order)

    reverse_order = [0] * total_blocks
    for i in range(total_blocks):
        current_pos = order[i]
        reverse_order[current_pos] = i

    return encrypt_image(scrambled_img, reverse_order)

if __name__ == "__main__":
    img = cv2.imread("input.jpg")

    if img is None:
        print("Помилка: файл input.jpg не знайдено!")
        exit()

    img = cv2.resize(img, (640, 480))

    total_blocks = ROWS * COLS

    order = make_shuffle_order(total_blocks, KEY)

    encrypted_img = encrypt_image(img, order)

    decrypted_img = decrypt_image(encrypted_img, order)

    result = np.hstack([img, encrypted_img, decrypted_img])

    cv2.imwrite("comparison_result.png", result)
    cv2.imshow("Original | Encrypted | Decrypted", result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()