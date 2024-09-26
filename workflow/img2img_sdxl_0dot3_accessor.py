from enum import Enum
from workflow.node_accessor import NodesAccessor


class Img2ImgSdxl0Dot3Accessor(NodesAccessor):
    WORKFLOW_FILE = "img2img_sdxl_0.3_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_VAE_DECODE = "8"
        NODE_SAVE_IMAGE = "9"
        NODE_LOAD_CHECKPOINT_BASE = "14"
        NODE_POSITIVETEXTENCODESDXL = "16"
        NODE_NEGATIVETEXTENCODESDXL = "19"
        NODE_KSAMPLER = "36"
        NODE_LOAD_VAE = "37"
        NODE_LOAD_IMAGE = "38"
        NODE_VAE_ENCODE = "39"
        NODE_UPSCALE_IMAGE = "40"

    class VAEDecode008VaeDecode:

        def __init__(self, outer):
            self._outer = outer

    class SaveImage009SaveImage:

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"] = value  # noqa

    class CheckpointLoaderSimple014LoadCheckpointBase:

        def __init__(self, outer):
            self._outer = outer

        @property
        def ckpt_name(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_CHECKPOINT_BASE.value]["inputs"]["ckpt_name"]  # noqa

        @ckpt_name.setter
        def ckpt_name(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_CHECKPOINT_BASE.value]["inputs"]["ckpt_name"] = value  # noqa

    class CLIPTextEncodeSDXL016Positivetextencodesdxl:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["height"] = value  # noqa

        @property
        def crop_w(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["crop_w"]  # noqa

        @crop_w.setter
        def crop_w(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["crop_w"] = value  # noqa

        @property
        def crop_h(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["crop_h"]  # noqa

        @crop_h.setter
        def crop_h(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["crop_h"] = value  # noqa

        @property
        def target_width(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["target_width"]  # noqa

        @target_width.setter
        def target_width(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["target_width"] = value  # noqa

        @property
        def target_height(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["target_height"]  # noqa

        @target_height.setter
        def target_height(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["target_height"] = value  # noqa

        @property
        def text_g(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["text_g"]  # noqa

        @text_g.setter
        def text_g(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["text_g"] = value  # noqa

        @property
        def text_l(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["text_l"]  # noqa

        @text_l.setter
        def text_l(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_POSITIVETEXTENCODESDXL.value]["inputs"]["text_l"] = value  # noqa

    class CLIPTextEncodeSDXL019Negativetextencodesdxl:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["height"] = value  # noqa

        @property
        def crop_w(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["crop_w"]  # noqa

        @crop_w.setter
        def crop_w(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["crop_w"] = value  # noqa

        @property
        def crop_h(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["crop_h"]  # noqa

        @crop_h.setter
        def crop_h(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["crop_h"] = value  # noqa

        @property
        def target_width(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["target_width"]  # noqa

        @target_width.setter
        def target_width(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["target_width"] = value  # noqa

        @property
        def target_height(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["target_height"]  # noqa

        @target_height.setter
        def target_height(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["target_height"] = value  # noqa

        @property
        def text_g(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["text_g"]  # noqa

        @text_g.setter
        def text_g(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["text_g"] = value  # noqa

        @property
        def text_l(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["text_l"]  # noqa

        @text_l.setter
        def text_l(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_NEGATIVETEXTENCODESDXL.value]["inputs"]["text_l"] = value  # noqa

    class KSampler036Ksampler:

        def __init__(self, outer):
            self._outer = outer

        @property
        def seed(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["seed"]  # noqa

        @seed.setter
        def seed(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def denoise(self) -> float:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["denoise"]  # noqa

        @denoise.setter
        def denoise(self, value: float):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["denoise"] = value  # noqa

    class VAELoader037LoadVae:

        def __init__(self, outer):
            self._outer = outer

        @property
        def vae_name(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"]  # noqa

        @vae_name.setter
        def vae_name(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"] = value  # noqa

    class LoadImage038LoadImage:

        def __init__(self, outer):
            self._outer = outer

        @property
        def image(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_IMAGE.value]["inputs"]["image"]  # noqa

        @image.setter
        def image(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_IMAGE.value]["inputs"]["image"] = value  # noqa

        @property
        def upload(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_IMAGE.value]["inputs"]["upload"]  # noqa

        @upload.setter
        def upload(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_LOAD_IMAGE.value]["inputs"]["upload"] = value  # noqa

    class VAEEncode039VaeEncode:

        def __init__(self, outer):
            self._outer = outer

    class ImageScale040UpscaleImage:

        def __init__(self, outer):
            self._outer = outer

        @property
        def upscale_method(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["upscale_method"]  # noqa

        @upscale_method.setter
        def upscale_method(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["upscale_method"] = value  # noqa

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["height"] = value  # noqa

        @property
        def crop(self) -> str:
            return self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["crop"]  # noqa

        @crop.setter
        def crop(self, value: str):
            self._outer.nodes_dict[Img2ImgSdxl0Dot3Accessor.NodeIndexes.NODE_UPSCALE_IMAGE.value]["inputs"]["crop"] = value  # noqa

    def __init__(self):
        super().__init__(Img2ImgSdxl0Dot3Accessor.WORKFLOW_FILE)
        self._vae_decode: Img2ImgSdxl0Dot3Accessor.VAEDecode008VaeDecode = Img2ImgSdxl0Dot3Accessor.VAEDecode008VaeDecode(self)  # noqa
        self._save_image: Img2ImgSdxl0Dot3Accessor.SaveImage009SaveImage = Img2ImgSdxl0Dot3Accessor.SaveImage009SaveImage(self)  # noqa
        self._load_checkpoint_base: Img2ImgSdxl0Dot3Accessor.CheckpointLoaderSimple014LoadCheckpointBase = Img2ImgSdxl0Dot3Accessor.CheckpointLoaderSimple014LoadCheckpointBase(self)  # noqa
        self._positivetextencodesdxl: Img2ImgSdxl0Dot3Accessor.CLIPTextEncodeSDXL016Positivetextencodesdxl = Img2ImgSdxl0Dot3Accessor.CLIPTextEncodeSDXL016Positivetextencodesdxl(self)  # noqa
        self._negativetextencodesdxl: Img2ImgSdxl0Dot3Accessor.CLIPTextEncodeSDXL019Negativetextencodesdxl = Img2ImgSdxl0Dot3Accessor.CLIPTextEncodeSDXL019Negativetextencodesdxl(self)  # noqa
        self._ksampler: Img2ImgSdxl0Dot3Accessor.KSampler036Ksampler = Img2ImgSdxl0Dot3Accessor.KSampler036Ksampler(self)  # noqa
        self._load_vae: Img2ImgSdxl0Dot3Accessor.VAELoader037LoadVae = Img2ImgSdxl0Dot3Accessor.VAELoader037LoadVae(self)  # noqa
        self._load_image: Img2ImgSdxl0Dot3Accessor.LoadImage038LoadImage = Img2ImgSdxl0Dot3Accessor.LoadImage038LoadImage(self)  # noqa
        self._vae_encode: Img2ImgSdxl0Dot3Accessor.VAEEncode039VaeEncode = Img2ImgSdxl0Dot3Accessor.VAEEncode039VaeEncode(self)  # noqa
        self._upscale_image: Img2ImgSdxl0Dot3Accessor.ImageScale040UpscaleImage = Img2ImgSdxl0Dot3Accessor.ImageScale040UpscaleImage(self)  # noqa

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
    def load_checkpoint_base(self):
        return self._load_checkpoint_base

    @load_checkpoint_base.setter
    def load_checkpoint_base(self, value):
        self._load_checkpoint_base = value

    @property
    def positivetextencodesdxl(self):
        return self._positivetextencodesdxl

    @positivetextencodesdxl.setter
    def positivetextencodesdxl(self, value):
        self._positivetextencodesdxl = value

    @property
    def negativetextencodesdxl(self):
        return self._negativetextencodesdxl

    @negativetextencodesdxl.setter
    def negativetextencodesdxl(self, value):
        self._negativetextencodesdxl = value

    @property
    def ksampler(self):
        return self._ksampler

    @ksampler.setter
    def ksampler(self, value):
        self._ksampler = value

    @property
    def load_vae(self):
        return self._load_vae

    @load_vae.setter
    def load_vae(self, value):
        self._load_vae = value

    @property
    def load_image(self):
        return self._load_image

    @load_image.setter
    def load_image(self, value):
        self._load_image = value

    @property
    def vae_encode(self):
        return self._vae_encode

    @vae_encode.setter
    def vae_encode(self, value):
        self._vae_encode = value

    @property
    def upscale_image(self):
        return self._upscale_image

    @upscale_image.setter
    def upscale_image(self, value):
        self._upscale_image = value
