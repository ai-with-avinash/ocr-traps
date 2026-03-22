import os, random, shutil

# Adjust these paths to your actual locations
task1_dir = "/Users/avinash/Downloads/SROIE2019/0325updated.task1train(626p)"  # images
task2_dir = "/Users/avinash/Downloads/SROIE2019/0325updated.task2train(626p)"  # ground truth text

receipts_dest = "test-dataset/06_mixed_content/receipts"
gt_dest = "test-dataset/ground_truth/06_mixed_content"
os.makedirs(receipts_dest, exist_ok=True)
os.makedirs(gt_dest, exist_ok=True)

# Find all images
images = [f for f in os.listdir(task1_dir) if f.endswith(('.jpg', '.png'))]
samples = random.sample(images, min(10, len(images)))

for img in samples:
    stem = os.path.splitext(img)[0]
    
    # Copy image
    shutil.copy2(os.path.join(task1_dir, img), os.path.join(receipts_dest, img))
    
    # Find and convert ground truth
    # Task2 files usually have same name as image but .txt extension
    txt_file = os.path.join(task2_dir, stem + ".txt")
    if os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = []
            for line in f:
                parts = line.strip().split(",", 8)
                if len(parts) >= 9:
                    lines.append(parts[8])  # text after 8 coordinates
                elif line.strip():
                    lines.append(line.strip())
        
        with open(os.path.join(gt_dest, stem + "_gt.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  ✅ {img} → {len(lines)} lines")
    else:
        print(f"  ⚠ No ground truth found for {img}")

print(f"\nDone! {len(samples)} receipts copied.")