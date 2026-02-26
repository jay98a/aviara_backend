from huggingface_hub import hf_hub_download

MODEL_DIR = "./models"
MODEL_NAME = "efficientnetv2s.h5"

model_path = hf_hub_download(
    repo_id="Miguel764/efficientnetv2s-skin-cancer-classifier",
    filename=MODEL_NAME,
    local_dir=MODEL_DIR,
    local_dir_use_symlinks=False  # important for Docker / portability
)

print("Saved at:", model_path)
