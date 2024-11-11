from enum import Enum
from workflow.node_accessor import NodesAccessor


class InpaintingSdxl0Dot4Accessor(NodesAccessor):
    WORKFLOW_FILE = "inpainting_sdxl_0.4_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_BASE_IMAGE = "1"
        NODE_MASK_IMAGE = "2"
        NODE_VAE_ENCODE_FOR_INPAINTING = "4"
        NODE_LOAD_CHECKPOINT = "5"
        NODE_LOAD_DIFFUSION_MODEL = "6"
        NODE_LOAD_LORA = "7"
        NODE_VAE_ENCODE = "8"
        NODE_POSITIVE_PROMPT = "9"
        NODE_NEGATIVE_PROMPT = "10"
        NODE_MODELSAMPLINGDISCRETE = "11"
        NODE_KSAMPLER = "12"
        NODE_VAE_DECODE = "13"
        NODE_SAVE_IMAGE = "14"
        NODE_SET_LATENT_NOISE_MASK = "15"

    class LoadImage001BaseImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def image(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_BASE_IMAGE.value]["inputs"]["image"]  # noqa

        @image.setter
        def image(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_BASE_IMAGE.value]["inputs"]["image"] = value  # noqa

        @property
        def upload(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_BASE_IMAGE.value]["inputs"]["upload"]  # noqa

        @upload.setter
        def upload(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_BASE_IMAGE.value]["inputs"]["upload"] = value  # noqa

    class LoadImage002MaskImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def image(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MASK_IMAGE.value]["inputs"]["image"]  # noqa

        @image.setter
        def image(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MASK_IMAGE.value]["inputs"]["image"] = value  # noqa

        @property
        def upload(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MASK_IMAGE.value]["inputs"]["upload"]  # noqa

        @upload.setter
        def upload(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MASK_IMAGE.value]["inputs"]["upload"] = value  # noqa

    class VAEEncodeForInpaint004VaeEncodeForInpainting:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def grow_mask_by(self) -> int:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_VAE_ENCODE_FOR_INPAINTING.value]["inputs"]["grow_mask_by"]  # noqa

        @grow_mask_by.setter
        def grow_mask_by(self, value: int):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_VAE_ENCODE_FOR_INPAINTING.value]["inputs"]["grow_mask_by"] = value  # noqa

    class CheckpointLoaderSimple005LoadCheckpoint:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def ckpt_name(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_CHECKPOINT.value]["inputs"]["ckpt_name"]  # noqa

        @ckpt_name.setter
        def ckpt_name(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_CHECKPOINT.value]["inputs"]["ckpt_name"] = value  # noqa

    class UNETLoader006LoadDiffusionModel:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def unet_name(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"]  # noqa

        @unet_name.setter
        def unet_name(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"] = value  # noqa

        @property
        def weight_dtype(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"]  # noqa

        @weight_dtype.setter
        def weight_dtype(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"] = value  # noqa

    class LoraLoader007LoadLora:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def lora_name(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_LORA.value]["inputs"]["lora_name"]  # noqa

        @lora_name.setter
        def lora_name(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_LORA.value]["inputs"]["lora_name"] = value  # noqa

        @property
        def strength_model(self) -> int:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_LORA.value]["inputs"]["strength_model"]  # noqa

        @strength_model.setter
        def strength_model(self, value: int):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_LORA.value]["inputs"]["strength_model"] = value  # noqa

        @property
        def strength_clip(self) -> int:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_LORA.value]["inputs"]["strength_clip"]  # noqa

        @strength_clip.setter
        def strength_clip(self, value: int):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_LORA.value]["inputs"]["strength_clip"] = value  # noqa

    class VAEEncode008VaeEncode:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class CLIPTextEncode009PositivePrompt:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_POSITIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_POSITIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class CLIPTextEncode010NegativePrompt:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_NEGATIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_NEGATIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class ModelSamplingDiscrete011Modelsamplingdiscrete:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def sampling(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MODELSAMPLINGDISCRETE.value]["inputs"]["sampling"]  # noqa

        @sampling.setter
        def sampling(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MODELSAMPLINGDISCRETE.value]["inputs"]["sampling"] = value  # noqa

        @property
        def zsnr(self) -> bool:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MODELSAMPLINGDISCRETE.value]["inputs"]["zsnr"]  # noqa

        @zsnr.setter
        def zsnr(self, value: bool):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_MODELSAMPLINGDISCRETE.value]["inputs"]["zsnr"] = value  # noqa

    class KSampler012Ksampler:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def seed(self) -> int:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["seed"]  # noqa

        @seed.setter
        def seed(self, value: int):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def denoise(self) -> int:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["denoise"]  # noqa

        @denoise.setter
        def denoise(self, value: int):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["denoise"] = value  # noqa

    class VAEDecode013VaeDecode:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class SaveImage014SaveImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[InpaintingSdxl0Dot4Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"] = value  # noqa

    class SetLatentNoiseMask015SetLatentNoiseMask:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    def __init__(self):
        super().__init__(InpaintingSdxl0Dot4Accessor.WORKFLOW_FILE)
        self._base_image: InpaintingSdxl0Dot4Accessor.LoadImage001BaseImage = InpaintingSdxl0Dot4Accessor.LoadImage001BaseImage(self)  # noqa
        self._mask_image: InpaintingSdxl0Dot4Accessor.LoadImage002MaskImage = InpaintingSdxl0Dot4Accessor.LoadImage002MaskImage(self)  # noqa
        self._vae_encode_for_inpainting: InpaintingSdxl0Dot4Accessor.VAEEncodeForInpaint004VaeEncodeForInpainting = InpaintingSdxl0Dot4Accessor.VAEEncodeForInpaint004VaeEncodeForInpainting(self)  # noqa
        self._load_checkpoint: InpaintingSdxl0Dot4Accessor.CheckpointLoaderSimple005LoadCheckpoint = InpaintingSdxl0Dot4Accessor.CheckpointLoaderSimple005LoadCheckpoint(self)  # noqa
        self._load_diffusion_model: InpaintingSdxl0Dot4Accessor.UNETLoader006LoadDiffusionModel = InpaintingSdxl0Dot4Accessor.UNETLoader006LoadDiffusionModel(self)  # noqa
        self._load_lora: InpaintingSdxl0Dot4Accessor.LoraLoader007LoadLora = InpaintingSdxl0Dot4Accessor.LoraLoader007LoadLora(self)  # noqa
        self._vae_encode: InpaintingSdxl0Dot4Accessor.VAEEncode008VaeEncode = InpaintingSdxl0Dot4Accessor.VAEEncode008VaeEncode(self)  # noqa
        self._positive_prompt: InpaintingSdxl0Dot4Accessor.CLIPTextEncode009PositivePrompt = InpaintingSdxl0Dot4Accessor.CLIPTextEncode009PositivePrompt(self)  # noqa
        self._negative_prompt: InpaintingSdxl0Dot4Accessor.CLIPTextEncode010NegativePrompt = InpaintingSdxl0Dot4Accessor.CLIPTextEncode010NegativePrompt(self)  # noqa
        self._modelsamplingdiscrete: InpaintingSdxl0Dot4Accessor.ModelSamplingDiscrete011Modelsamplingdiscrete = InpaintingSdxl0Dot4Accessor.ModelSamplingDiscrete011Modelsamplingdiscrete(self)  # noqa
        self._ksampler: InpaintingSdxl0Dot4Accessor.KSampler012Ksampler = InpaintingSdxl0Dot4Accessor.KSampler012Ksampler(self)  # noqa
        self._vae_decode: InpaintingSdxl0Dot4Accessor.VAEDecode013VaeDecode = InpaintingSdxl0Dot4Accessor.VAEDecode013VaeDecode(self)  # noqa
        self._save_image: InpaintingSdxl0Dot4Accessor.SaveImage014SaveImage = InpaintingSdxl0Dot4Accessor.SaveImage014SaveImage(self)  # noqa
        self._set_latent_noise_mask: InpaintingSdxl0Dot4Accessor.SetLatentNoiseMask015SetLatentNoiseMask = InpaintingSdxl0Dot4Accessor.SetLatentNoiseMask015SetLatentNoiseMask(self)  # noqa

    @property
    def base_image(self):
        return self._base_image

    @base_image.setter
    def base_image(self, value):
        self._base_image = value

    @property
    def mask_image(self):
        return self._mask_image

    @mask_image.setter
    def mask_image(self, value):
        self._mask_image = value

    @property
    def vae_encode_for_inpainting(self):
        return self._vae_encode_for_inpainting

    @vae_encode_for_inpainting.setter
    def vae_encode_for_inpainting(self, value):
        self._vae_encode_for_inpainting = value

    @property
    def load_checkpoint(self):
        return self._load_checkpoint

    @load_checkpoint.setter
    def load_checkpoint(self, value):
        self._load_checkpoint = value

    @property
    def load_diffusion_model(self):
        return self._load_diffusion_model

    @load_diffusion_model.setter
    def load_diffusion_model(self, value):
        self._load_diffusion_model = value

    @property
    def load_lora(self):
        return self._load_lora

    @load_lora.setter
    def load_lora(self, value):
        self._load_lora = value

    @property
    def vae_encode(self):
        return self._vae_encode

    @vae_encode.setter
    def vae_encode(self, value):
        self._vae_encode = value

    @property
    def positive_prompt(self):
        return self._positive_prompt

    @positive_prompt.setter
    def positive_prompt(self, value):
        self._positive_prompt = value

    @property
    def negative_prompt(self):
        return self._negative_prompt

    @negative_prompt.setter
    def negative_prompt(self, value):
        self._negative_prompt = value

    @property
    def modelsamplingdiscrete(self):
        return self._modelsamplingdiscrete

    @modelsamplingdiscrete.setter
    def modelsamplingdiscrete(self, value):
        self._modelsamplingdiscrete = value

    @property
    def ksampler(self):
        return self._ksampler

    @ksampler.setter
    def ksampler(self, value):
        self._ksampler = value

    @property
    def vae_decode(self):
        return self._vae_decode

    @vae_decode.setter
    def vae_decode(self, value):
        self._vae_decode = value

    @property
    def save_image(self):
        return self._save_image

    @save_image.setter
    def save_image(self, value):
        self._save_image = value

    @property
    def set_latent_noise_mask(self):
        return self._set_latent_noise_mask

    @set_latent_noise_mask.setter
    def set_latent_noise_mask(self, value):
        self._set_latent_noise_mask = value
