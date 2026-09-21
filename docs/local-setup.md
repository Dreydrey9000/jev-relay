# Reproducible local setup

The supported optional worker is Laya-MLX on Apple Silicon. Core routing also works without a local model, including on Linux. Do not try this worker on a CUDA or Intel machine.

Use Python 3.12 and a dedicated environment outside synced folders. From the repository:

```sh
python3.12 -m venv .venv-laya
.venv-laya/bin/python -m pip install -r requirements-laya.lock
.venv-laya/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('aac6fef/laya-mlx', revision='20aed815fc6acde75733882e7ec0e3f28aeb9717', allow_patterns=['model.safetensors','rl_agent_config.json','encoder/config.json','tokenizer/*','mlx_config.json'], local_dir='models/laya-checkpoint', max_workers=1)"
```

Reserve room for the environment, checkpoint, download cache and ordinary operating-system needs. The weights alone are 842,609,225 bytes. Download time depends on connection speed; Hugging Face can retain partial downloads. Do not disable resource protections to finish a download.

Expected SHA-256 of `model.safetensors`:

```text
b9c07bf14be2fa5c78a9193a3e6d840ac80e89e62fc40f425834c3d8a6eaa3de
```

Configure the absolute environment, model and guard paths as shown in the README. Run the public example through `jev-relay`; a model answer still has `requires_review: true`. A resource warning requires a current, explicit owner acknowledgement. Never persist `--ack-resource-warning` in the launcher or config.

To reproduce the 24-case pilot after reviewing current resource conditions:

```sh
python3 scripts/evaluate.py --config ~/.config/jev-relay/config.json --output eval/my-local-run.json
```

If a soft warning is explicitly approved, add `--ack-resource-warning` for that bounded run. Hard blocks remain in force. Each case starts a new monitored worker and unloads on exit; the reported latency is cold round-trip time, not warm model latency. Evaluation stops after two consecutive unavailable results. The fixtures contain public synthetic examples. Do not replace them with private customer records and commit the resulting logs.

The pinned optional runtime comes from the upstream [Laya-MLX repository](https://github.com/mizorewww/laya-mlx/tree/fc1df62828a3fedf4d8229fdac1cbd85f1cdf337), and the [checkpoint](https://huggingface.co/aac6fef/laya-mlx/tree/20aed815fc6acde75733882e7ec0e3f28aeb9717) is a separate download. Their licenses and model behavior are separate from this router's MIT license.
