from enum import Enum
from workflow.node_accessor import NodesAccessor


class Flux1Dot0Accessor(NodesAccessor):
    WORKFLOW_FILE = "flux_1.0_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_CLIP_TEXT_ENCODE_POSITIVE_PROMPT = "6"
        NODE_VAE_DECODE = "8"
        NODE_SAVE_IMAGE = "9"
        NODE_LOAD_VAE = "10"
        NODE_DUALCLIPLOADER = "11"
        NODE_LOAD_DIFFUSION_MODEL = "12"
        NODE_SAMPLERCUSTOMADVANCED = "13"
        NODE_KSAMPLERSELECT = "16"
        NODE_BASICSCHEDULER = "17"
        NODE_BASICGUIDER = "22"
        NODE_RANDOMNOISE = "25"
        NODE_FLUXGUIDANCE = "26"
        NODE_EMPTYSD3LATENTIMAGE = "27"
        NODE_MODELSAMPLINGFLUX = "30"

    class CLIPTextEncode006ClipTextEncodePositivePrompt:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_CLIP_TEXT_ENCODE_POSITIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_CLIP_TEXT_ENCODE_POSITIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class VAEDecode008VaeDecode:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class SaveImage009SaveImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"] = value  # noqa

    class VAELoader010LoadVae:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def vae_name(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"]  # noqa

        @vae_name.setter
        def vae_name(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"] = value  # noqa

    class DualCLIPLoader011Dualcliploader:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def clip_name1(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name1"]  # noqa

        @clip_name1.setter
        def clip_name1(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name1"] = value  # noqa

        @property
        def clip_name2(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name2"]  # noqa

        @clip_name2.setter
        def clip_name2(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name2"] = value  # noqa

        @property
        def type(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["type"]  # noqa

        @type.setter
        def type(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["type"] = value  # noqa

    class UNETLoader012LoadDiffusionModel:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def unet_name(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"]  # noqa

        @unet_name.setter
        def unet_name(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"] = value  # noqa

        @property
        def weight_dtype(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"]  # noqa

        @weight_dtype.setter
        def weight_dtype(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"] = value  # noqa

    class SamplerCustomAdvanced013Samplercustomadvanced:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class KSamplerSelect016Ksamplerselect:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_KSAMPLERSELECT.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_KSAMPLERSELECT.value]["inputs"]["sampler_name"] = value  # noqa

    class BasicScheduler017Basicscheduler:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_BASICSCHEDULER.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_BASICSCHEDULER.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_BASICSCHEDULER.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_BASICSCHEDULER.value]["inputs"]["steps"] = value  # noqa

        @property
        def denoise(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_BASICSCHEDULER.value]["inputs"]["denoise"]  # noqa

        @denoise.setter
        def denoise(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_BASICSCHEDULER.value]["inputs"]["denoise"] = value  # noqa

    class BasicGuider022Basicguider:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class RandomNoise025Randomnoise:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_RANDOMNOISE.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_RANDOMNOISE.value]["inputs"]["noise_seed"] = value  # noqa

    class FluxGuidance026Fluxguidance:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def guidance(self) -> float:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_FLUXGUIDANCE.value]["inputs"]["guidance"]  # noqa

        @guidance.setter
        def guidance(self, value: float):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_FLUXGUIDANCE.value]["inputs"]["guidance"] = value  # noqa

    class EmptySD3LatentImage027Emptysd3Latentimage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_EMPTYSD3LATENTIMAGE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_EMPTYSD3LATENTIMAGE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_EMPTYSD3LATENTIMAGE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_EMPTYSD3LATENTIMAGE.value]["inputs"]["height"] = value  # noqa

        @property
        def batch_size(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_EMPTYSD3LATENTIMAGE.value]["inputs"]["batch_size"]  # noqa

        @batch_size.setter
        def batch_size(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_EMPTYSD3LATENTIMAGE.value]["inputs"]["batch_size"] = value  # noqa

    class ModelSamplingFlux030Modelsamplingflux:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def max_shift(self) -> float:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["max_shift"]  # noqa

        @max_shift.setter
        def max_shift(self, value: float):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["max_shift"] = value  # noqa

        @property
        def base_shift(self) -> float:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["base_shift"]  # noqa

        @base_shift.setter
        def base_shift(self, value: float):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["base_shift"] = value  # noqa

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[Flux1Dot0Accessor.NodeIndexes.NODE_MODELSAMPLINGFLUX.value]["inputs"]["height"] = value  # noqa

    def __init__(self):
        super().__init__(Flux1Dot0Accessor.WORKFLOW_FILE)
        self._clip_text_encode_positive_prompt: Flux1Dot0Accessor.CLIPTextEncode006ClipTextEncodePositivePrompt = Flux1Dot0Accessor.CLIPTextEncode006ClipTextEncodePositivePrompt(self)  # noqa
        self._vae_decode: Flux1Dot0Accessor.VAEDecode008VaeDecode = Flux1Dot0Accessor.VAEDecode008VaeDecode(self)  # noqa
        self._save_image: Flux1Dot0Accessor.SaveImage009SaveImage = Flux1Dot0Accessor.SaveImage009SaveImage(self)  # noqa
        self._load_vae: Flux1Dot0Accessor.VAELoader010LoadVae = Flux1Dot0Accessor.VAELoader010LoadVae(self)  # noqa
        self._dualcliploader: Flux1Dot0Accessor.DualCLIPLoader011Dualcliploader = Flux1Dot0Accessor.DualCLIPLoader011Dualcliploader(self)  # noqa
        self._load_diffusion_model: Flux1Dot0Accessor.UNETLoader012LoadDiffusionModel = Flux1Dot0Accessor.UNETLoader012LoadDiffusionModel(self)  # noqa
        self._samplercustomadvanced: Flux1Dot0Accessor.SamplerCustomAdvanced013Samplercustomadvanced = Flux1Dot0Accessor.SamplerCustomAdvanced013Samplercustomadvanced(self)  # noqa
        self._ksamplerselect: Flux1Dot0Accessor.KSamplerSelect016Ksamplerselect = Flux1Dot0Accessor.KSamplerSelect016Ksamplerselect(self)  # noqa
        self._basicscheduler: Flux1Dot0Accessor.BasicScheduler017Basicscheduler = Flux1Dot0Accessor.BasicScheduler017Basicscheduler(self)  # noqa
        self._basicguider: Flux1Dot0Accessor.BasicGuider022Basicguider = Flux1Dot0Accessor.BasicGuider022Basicguider(self)  # noqa
        self._randomnoise: Flux1Dot0Accessor.RandomNoise025Randomnoise = Flux1Dot0Accessor.RandomNoise025Randomnoise(self)  # noqa
        self._fluxguidance: Flux1Dot0Accessor.FluxGuidance026Fluxguidance = Flux1Dot0Accessor.FluxGuidance026Fluxguidance(self)  # noqa
        self._emptysd3latentimage: Flux1Dot0Accessor.EmptySD3LatentImage027Emptysd3Latentimage = Flux1Dot0Accessor.EmptySD3LatentImage027Emptysd3Latentimage(self)  # noqa
        self._modelsamplingflux: Flux1Dot0Accessor.ModelSamplingFlux030Modelsamplingflux = Flux1Dot0Accessor.ModelSamplingFlux030Modelsamplingflux(self)  # noqa

    @property
    def clip_text_encode_positive_prompt(self):
        return self._clip_text_encode_positive_prompt

    @clip_text_encode_positive_prompt.setter
    def clip_text_encode_positive_prompt(self, value):
        self._clip_text_encode_positive_prompt = value

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
    def load_vae(self):
        return self._load_vae

    @load_vae.setter
    def load_vae(self, value):
        self._load_vae = value

    @property
    def dualcliploader(self):
        return self._dualcliploader

    @dualcliploader.setter
    def dualcliploader(self, value):
        self._dualcliploader = value

    @property
    def load_diffusion_model(self):
        return self._load_diffusion_model

    @load_diffusion_model.setter
    def load_diffusion_model(self, value):
        self._load_diffusion_model = value

    @property
    def samplercustomadvanced(self):
        return self._samplercustomadvanced

    @samplercustomadvanced.setter
    def samplercustomadvanced(self, value):
        self._samplercustomadvanced = value

    @property
    def ksamplerselect(self):
        return self._ksamplerselect

    @ksamplerselect.setter
    def ksamplerselect(self, value):
        self._ksamplerselect = value

    @property
    def basicscheduler(self):
        return self._basicscheduler

    @basicscheduler.setter
    def basicscheduler(self, value):
        self._basicscheduler = value

    @property
    def basicguider(self):
        return self._basicguider

    @basicguider.setter
    def basicguider(self, value):
        self._basicguider = value

    @property
    def randomnoise(self):
        return self._randomnoise

    @randomnoise.setter
    def randomnoise(self, value):
        self._randomnoise = value

    @property
    def fluxguidance(self):
        return self._fluxguidance

    @fluxguidance.setter
    def fluxguidance(self, value):
        self._fluxguidance = value

    @property
    def emptysd3latentimage(self):
        return self._emptysd3latentimage

    @emptysd3latentimage.setter
    def emptysd3latentimage(self, value):
        self._emptysd3latentimage = value

    @property
    def modelsamplingflux(self):
        return self._modelsamplingflux

    @modelsamplingflux.setter
    def modelsamplingflux(self, value):
        self._modelsamplingflux = value
