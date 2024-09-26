from enum import Enum
from workflow.node_accessor import NodesAccessor


class ComfyuiDefaultAccessor(NodesAccessor):
    WORKFLOW_FILE = "comfyui_default_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_KSAMPLER = "3"
        NODE_LOAD_CHECKPOINT = "4"
        NODE_EMPTY_LATENT_IMAGE = "5"
        NODE_POSITIVE_PROMPT = "6"
        NODE_NEGATIVE_PROMPT = "7"
        NODE_VAE_DECODE = "8"
        NODE_SAVE_IMAGE = "9"

    class KSampler003Ksampler:

        def __init__(self, outer):
            self._outer = outer

        @property
        def seed(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["seed"]  # noqa

        @seed.setter
        def seed(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def denoise(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["denoise"]  # noqa

        @denoise.setter
        def denoise(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_KSAMPLER.value]["inputs"]["denoise"] = value  # noqa

    class CheckpointLoaderSimple004LoadCheckpoint:

        def __init__(self, outer):
            self._outer = outer

        @property
        def ckpt_name(self) -> str:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_LOAD_CHECKPOINT.value]["inputs"]["ckpt_name"]  # noqa

        @ckpt_name.setter
        def ckpt_name(self, value: str):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_LOAD_CHECKPOINT.value]["inputs"]["ckpt_name"] = value  # noqa

    class EmptyLatentImage005EmptyLatentImage:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["height"] = value  # noqa

        @property
        def batch_size(self) -> int:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["batch_size"]  # noqa

        @batch_size.setter
        def batch_size(self, value: int):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["batch_size"] = value  # noqa

    class CLIPTextEncode006PositivePrompt:

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_POSITIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_POSITIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class CLIPTextEncode007NegativePrompt:

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_NEGATIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_NEGATIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class VAEDecode008VaeDecode:

        def __init__(self, outer):
            self._outer = outer

    class SaveImage009SaveImage:

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[ComfyuiDefaultAccessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"] = value  # noqa

    def __init__(self):
        super().__init__(ComfyuiDefaultAccessor.WORKFLOW_FILE)
        self._ksampler: ComfyuiDefaultAccessor.KSampler003Ksampler = ComfyuiDefaultAccessor.KSampler003Ksampler(self)  # noqa
        self._load_checkpoint: ComfyuiDefaultAccessor.CheckpointLoaderSimple004LoadCheckpoint = ComfyuiDefaultAccessor.CheckpointLoaderSimple004LoadCheckpoint(self)  # noqa
        self._empty_latent_image: ComfyuiDefaultAccessor.EmptyLatentImage005EmptyLatentImage = ComfyuiDefaultAccessor.EmptyLatentImage005EmptyLatentImage(self)  # noqa
        self._positive_prompt: ComfyuiDefaultAccessor.CLIPTextEncode006PositivePrompt = ComfyuiDefaultAccessor.CLIPTextEncode006PositivePrompt(self)  # noqa
        self._negative_prompt: ComfyuiDefaultAccessor.CLIPTextEncode007NegativePrompt = ComfyuiDefaultAccessor.CLIPTextEncode007NegativePrompt(self)  # noqa
        self._vae_decode: ComfyuiDefaultAccessor.VAEDecode008VaeDecode = ComfyuiDefaultAccessor.VAEDecode008VaeDecode(self)  # noqa
        self._save_image: ComfyuiDefaultAccessor.SaveImage009SaveImage = ComfyuiDefaultAccessor.SaveImage009SaveImage(self)  # noqa

    @property
    def ksampler(self):
        return self._ksampler

    @ksampler.setter
    def ksampler(self, value):
        self._ksampler = value

    @property
    def load_checkpoint(self):
        return self._load_checkpoint

    @load_checkpoint.setter
    def load_checkpoint(self, value):
        self._load_checkpoint = value

    @property
    def empty_latent_image(self):
        return self._empty_latent_image

    @empty_latent_image.setter
    def empty_latent_image(self, value):
        self._empty_latent_image = value

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
