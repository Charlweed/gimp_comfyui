from enum import Enum
from workflow.node_accessor import NodesAccessor


class FluxNegUpscaleSdxl0Dot4Accessor(NodesAccessor):
    WORKFLOW_FILE = "flux_neg_upscale_sdxl_0.4_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_POSITIVE_PROMPT = "6"
        NODE_LOAD_VAE = "10"
        NODE_DUALCLIPLOADER = "11"
        NODE_LOAD_DIFFUSION_MODEL = "12"
        NODE_TOBASICPIPE = "47"
        NODE_EMPTY_LATENT_IMAGE = "49"
        NODE_KSAMPLER_PASS2_ADVANCEDPIPE = "97"
        NODE_KSAMPLER_PASS1_ADVANCEDPIPE = "98"
        NODE_DYNAMICTHRESHOLDINGFULL = "100"
        NODE_NEGATIVE_PROMPT = "101"
        NODE_EDIT_BASICPIPE = "103"
        NODE_FROMBASICPIPE_V2 = "104"
        NODE_NEGATIVE_COND_PLACEHOLDER = "105"
        NODE_VAE_DECODE = "111"
        NODE_SD_4XUPSCALE_CONDITIONING = "121"
        NODE_EFFICIENT_LOADER = "122"
        NODE_ULTIMATE_SD_UPSCALE = "123"
        NODE_LOAD_UPSCALE_MODEL = "124"
        NODE_GET_IMAGE_SIZE__COUNT = "125"
        NODE_SAVE_IMAGE = "128"
        NODE_SAVE_IMAGE_01 = "129"

    class CLIPTextEncode006PositivePrompt:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_POSITIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_POSITIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class VAELoader010LoadVae:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def vae_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"]  # noqa

        @vae_name.setter
        def vae_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"] = value  # noqa

    class DualCLIPLoader011Dualcliploader:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def clip_name1(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name1"]  # noqa

        @clip_name1.setter
        def clip_name1(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name1"] = value  # noqa

        @property
        def clip_name2(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name2"]  # noqa

        @clip_name2.setter
        def clip_name2(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name2"] = value  # noqa

        @property
        def type(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["type"]  # noqa

        @type.setter
        def type(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["type"] = value  # noqa

    class UNETLoader012LoadDiffusionModel:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def unet_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"]  # noqa

        @unet_name.setter
        def unet_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"] = value  # noqa

        @property
        def weight_dtype(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"]  # noqa

        @weight_dtype.setter
        def weight_dtype(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"] = value  # noqa

    class ToBasicPipe047Tobasicpipe:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class EmptyLatentImage049EmptyLatentImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["height"] = value  # noqa

        @property
        def batch_size(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["batch_size"]  # noqa

        @batch_size.setter
        def batch_size(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["batch_size"] = value  # noqa

    class ImpactKSamplerAdvancedBasicPipe097KsamplerPass2Advancedpipe:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: bool):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: bool):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS2_ADVANCEDPIPE.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class ImpactKSamplerAdvancedBasicPipe098KsamplerPass1Advancedpipe:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: bool):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: bool):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_KSAMPLER_PASS1_ADVANCEDPIPE.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class DynamicThresholdingFull100Dynamicthresholdingfull:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def mimic_scale(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale"]  # noqa

        @mimic_scale.setter
        def mimic_scale(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale"] = value  # noqa

        @property
        def threshold_percentile(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["threshold_percentile"]  # noqa

        @threshold_percentile.setter
        def threshold_percentile(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["threshold_percentile"] = value  # noqa

        @property
        def mimic_mode(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_mode"]  # noqa

        @mimic_mode.setter
        def mimic_mode(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_mode"] = value  # noqa

        @property
        def mimic_scale_min(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale_min"]  # noqa

        @mimic_scale_min.setter
        def mimic_scale_min(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale_min"] = value  # noqa

        @property
        def cfg_mode(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_mode"]  # noqa

        @cfg_mode.setter
        def cfg_mode(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_mode"] = value  # noqa

        @property
        def cfg_scale_min(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_scale_min"]  # noqa

        @cfg_scale_min.setter
        def cfg_scale_min(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_scale_min"] = value  # noqa

        @property
        def sched_val(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["sched_val"]  # noqa

        @sched_val.setter
        def sched_val(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["sched_val"] = value  # noqa

        @property
        def separate_feature_channels(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["separate_feature_channels"]  # noqa

        @separate_feature_channels.setter
        def separate_feature_channels(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["separate_feature_channels"] = value  # noqa

        @property
        def scaling_startpoint(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["scaling_startpoint"]  # noqa

        @scaling_startpoint.setter
        def scaling_startpoint(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["scaling_startpoint"] = value  # noqa

        @property
        def variability_measure(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["variability_measure"]  # noqa

        @variability_measure.setter
        def variability_measure(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["variability_measure"] = value  # noqa

        @property
        def interpolate_phi(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["interpolate_phi"]  # noqa

        @interpolate_phi.setter
        def interpolate_phi(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["interpolate_phi"] = value  # noqa

    class CLIPTextEncode101NegativePrompt:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_NEGATIVE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_NEGATIVE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class EditBasicPipe103EditBasicpipe:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class FromBasicPipe_v2104FrombasicpipeV2:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class ImpactNegativeConditioningPlaceholder105NegativeCondPlaceholder:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class VAEDecode111VaeDecode:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class SD_4XUpscale_Conditioning121Sd4XupscaleConditioning:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def scale_ratio(self) -> float:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SD_4XUPSCALE_CONDITIONING.value]["inputs"]["scale_ratio"]  # noqa

        @scale_ratio.setter
        def scale_ratio(self, value: float):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SD_4XUPSCALE_CONDITIONING.value]["inputs"]["scale_ratio"] = value  # noqa

        @property
        def noise_augmentation(self) -> float:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SD_4XUPSCALE_CONDITIONING.value]["inputs"]["noise_augmentation"]  # noqa

        @noise_augmentation.setter
        def noise_augmentation(self, value: float):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SD_4XUPSCALE_CONDITIONING.value]["inputs"]["noise_augmentation"] = value  # noqa

    class EfficientLoader122EfficientLoader:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def ckpt_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["ckpt_name"]  # noqa

        @ckpt_name.setter
        def ckpt_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["ckpt_name"] = value  # noqa

        @property
        def vae_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["vae_name"]  # noqa

        @vae_name.setter
        def vae_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["vae_name"] = value  # noqa

        @property
        def clip_skip(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["clip_skip"]  # noqa

        @clip_skip.setter
        def clip_skip(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["clip_skip"] = value  # noqa

        @property
        def lora_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["lora_name"]  # noqa

        @lora_name.setter
        def lora_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["lora_name"] = value  # noqa

        @property
        def lora_model_strength(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["lora_model_strength"]  # noqa

        @lora_model_strength.setter
        def lora_model_strength(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["lora_model_strength"] = value  # noqa

        @property
        def lora_clip_strength(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["lora_clip_strength"]  # noqa

        @lora_clip_strength.setter
        def lora_clip_strength(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["lora_clip_strength"] = value  # noqa

        @property
        def positive(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["positive"]  # noqa

        @positive.setter
        def positive(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["positive"] = value  # noqa

        @property
        def negative(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["negative"]  # noqa

        @negative.setter
        def negative(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["negative"] = value  # noqa

        @property
        def token_normalization(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["token_normalization"]  # noqa

        @token_normalization.setter
        def token_normalization(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["token_normalization"] = value  # noqa

        @property
        def weight_interpretation(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["weight_interpretation"]  # noqa

        @weight_interpretation.setter
        def weight_interpretation(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["weight_interpretation"] = value  # noqa

        @property
        def empty_latent_width(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["empty_latent_width"]  # noqa

        @empty_latent_width.setter
        def empty_latent_width(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["empty_latent_width"] = value  # noqa

        @property
        def empty_latent_height(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["empty_latent_height"]  # noqa

        @empty_latent_height.setter
        def empty_latent_height(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["empty_latent_height"] = value  # noqa

        @property
        def batch_size(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["batch_size"]  # noqa

        @batch_size.setter
        def batch_size(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_EFFICIENT_LOADER.value]["inputs"]["batch_size"] = value  # noqa

    class UltimateSDUpscale123UltimateSdUpscale:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def upscale_by(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["upscale_by"]  # noqa

        @upscale_by.setter
        def upscale_by(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["upscale_by"] = value  # noqa

        @property
        def seed(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seed"]  # noqa

        @seed.setter
        def seed(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def denoise(self) -> float:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["denoise"]  # noqa

        @denoise.setter
        def denoise(self, value: float):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["denoise"] = value  # noqa

        @property
        def mode_type(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["mode_type"]  # noqa

        @mode_type.setter
        def mode_type(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["mode_type"] = value  # noqa

        @property
        def mask_blur(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["mask_blur"]  # noqa

        @mask_blur.setter
        def mask_blur(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["mask_blur"] = value  # noqa

        @property
        def tile_padding(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["tile_padding"]  # noqa

        @tile_padding.setter
        def tile_padding(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["tile_padding"] = value  # noqa

        @property
        def seam_fix_mode(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_mode"]  # noqa

        @seam_fix_mode.setter
        def seam_fix_mode(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_mode"] = value  # noqa

        @property
        def seam_fix_denoise(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_denoise"]  # noqa

        @seam_fix_denoise.setter
        def seam_fix_denoise(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_denoise"] = value  # noqa

        @property
        def seam_fix_width(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_width"]  # noqa

        @seam_fix_width.setter
        def seam_fix_width(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_width"] = value  # noqa

        @property
        def seam_fix_mask_blur(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_mask_blur"]  # noqa

        @seam_fix_mask_blur.setter
        def seam_fix_mask_blur(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_mask_blur"] = value  # noqa

        @property
        def seam_fix_padding(self) -> int:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_padding"]  # noqa

        @seam_fix_padding.setter
        def seam_fix_padding(self, value: int):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["seam_fix_padding"] = value  # noqa

        @property
        def force_uniform_tiles(self) -> bool:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["force_uniform_tiles"]  # noqa

        @force_uniform_tiles.setter
        def force_uniform_tiles(self, value: bool):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["force_uniform_tiles"] = value  # noqa

        @property
        def tiled_decode(self) -> bool:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["tiled_decode"]  # noqa

        @tiled_decode.setter
        def tiled_decode(self, value: bool):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_ULTIMATE_SD_UPSCALE.value]["inputs"]["tiled_decode"] = value  # noqa

    class UpscaleModelLoader124LoadUpscaleModel:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def model_name(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_UPSCALE_MODEL.value]["inputs"]["model_name"]  # noqa

        @model_name.setter
        def model_name(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_LOAD_UPSCALE_MODEL.value]["inputs"]["model_name"] = value  # noqa

    class GetImageSizeAndCount125GetImageSizeCount:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

    class SaveImage128SaveImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SAVE_IMAGE.value]["inputs"]["filename_prefix"] = value  # noqa

    class SaveImage129SaveImage:  # noqa PEP8

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SAVE_IMAGE_01.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[FluxNegUpscaleSdxl0Dot4Accessor.NodeIndexes.NODE_SAVE_IMAGE_01.value]["inputs"]["filename_prefix"] = value  # noqa

    def __init__(self):
        super().__init__(FluxNegUpscaleSdxl0Dot4Accessor.WORKFLOW_FILE)
        self._positive_prompt: FluxNegUpscaleSdxl0Dot4Accessor.CLIPTextEncode006PositivePrompt = FluxNegUpscaleSdxl0Dot4Accessor.CLIPTextEncode006PositivePrompt(self)  # noqa
        self._load_vae: FluxNegUpscaleSdxl0Dot4Accessor.VAELoader010LoadVae = FluxNegUpscaleSdxl0Dot4Accessor.VAELoader010LoadVae(self)  # noqa
        self._dualcliploader: FluxNegUpscaleSdxl0Dot4Accessor.DualCLIPLoader011Dualcliploader = FluxNegUpscaleSdxl0Dot4Accessor.DualCLIPLoader011Dualcliploader(self)  # noqa
        self._load_diffusion_model: FluxNegUpscaleSdxl0Dot4Accessor.UNETLoader012LoadDiffusionModel = FluxNegUpscaleSdxl0Dot4Accessor.UNETLoader012LoadDiffusionModel(self)  # noqa
        self._tobasicpipe: FluxNegUpscaleSdxl0Dot4Accessor.ToBasicPipe047Tobasicpipe = FluxNegUpscaleSdxl0Dot4Accessor.ToBasicPipe047Tobasicpipe(self)  # noqa
        self._empty_latent_image: FluxNegUpscaleSdxl0Dot4Accessor.EmptyLatentImage049EmptyLatentImage = FluxNegUpscaleSdxl0Dot4Accessor.EmptyLatentImage049EmptyLatentImage(self)  # noqa
        self._ksampler_pass2_advancedpipe: FluxNegUpscaleSdxl0Dot4Accessor.ImpactKSamplerAdvancedBasicPipe097KsamplerPass2Advancedpipe = FluxNegUpscaleSdxl0Dot4Accessor.ImpactKSamplerAdvancedBasicPipe097KsamplerPass2Advancedpipe(self)  # noqa
        self._ksampler_pass1_advancedpipe: FluxNegUpscaleSdxl0Dot4Accessor.ImpactKSamplerAdvancedBasicPipe098KsamplerPass1Advancedpipe = FluxNegUpscaleSdxl0Dot4Accessor.ImpactKSamplerAdvancedBasicPipe098KsamplerPass1Advancedpipe(self)  # noqa
        self._dynamicthresholdingfull: FluxNegUpscaleSdxl0Dot4Accessor.DynamicThresholdingFull100Dynamicthresholdingfull = FluxNegUpscaleSdxl0Dot4Accessor.DynamicThresholdingFull100Dynamicthresholdingfull(self)  # noqa
        self._negative_prompt: FluxNegUpscaleSdxl0Dot4Accessor.CLIPTextEncode101NegativePrompt = FluxNegUpscaleSdxl0Dot4Accessor.CLIPTextEncode101NegativePrompt(self)  # noqa
        self._edit_basicpipe: FluxNegUpscaleSdxl0Dot4Accessor.EditBasicPipe103EditBasicpipe = FluxNegUpscaleSdxl0Dot4Accessor.EditBasicPipe103EditBasicpipe(self)  # noqa
        self._frombasicpipe_v2: FluxNegUpscaleSdxl0Dot4Accessor.FromBasicPipe_v2104FrombasicpipeV2 = FluxNegUpscaleSdxl0Dot4Accessor.FromBasicPipe_v2104FrombasicpipeV2(self)  # noqa
        self._negative_cond_placeholder: FluxNegUpscaleSdxl0Dot4Accessor.ImpactNegativeConditioningPlaceholder105NegativeCondPlaceholder = FluxNegUpscaleSdxl0Dot4Accessor.ImpactNegativeConditioningPlaceholder105NegativeCondPlaceholder(self)  # noqa
        self._vae_decode: FluxNegUpscaleSdxl0Dot4Accessor.VAEDecode111VaeDecode = FluxNegUpscaleSdxl0Dot4Accessor.VAEDecode111VaeDecode(self)  # noqa
        self._sd_4xupscale_conditioning: FluxNegUpscaleSdxl0Dot4Accessor.SD_4XUpscale_Conditioning121Sd4XupscaleConditioning = FluxNegUpscaleSdxl0Dot4Accessor.SD_4XUpscale_Conditioning121Sd4XupscaleConditioning(self)  # noqa
        self._efficient_loader: FluxNegUpscaleSdxl0Dot4Accessor.EfficientLoader122EfficientLoader = FluxNegUpscaleSdxl0Dot4Accessor.EfficientLoader122EfficientLoader(self)  # noqa
        self._ultimate_sd_upscale: FluxNegUpscaleSdxl0Dot4Accessor.UltimateSDUpscale123UltimateSdUpscale = FluxNegUpscaleSdxl0Dot4Accessor.UltimateSDUpscale123UltimateSdUpscale(self)  # noqa
        self._load_upscale_model: FluxNegUpscaleSdxl0Dot4Accessor.UpscaleModelLoader124LoadUpscaleModel = FluxNegUpscaleSdxl0Dot4Accessor.UpscaleModelLoader124LoadUpscaleModel(self)  # noqa
        self._get_image_size__count: FluxNegUpscaleSdxl0Dot4Accessor.GetImageSizeAndCount125GetImageSizeCount = FluxNegUpscaleSdxl0Dot4Accessor.GetImageSizeAndCount125GetImageSizeCount(self)  # noqa
        self._save_image: FluxNegUpscaleSdxl0Dot4Accessor.SaveImage128SaveImage = FluxNegUpscaleSdxl0Dot4Accessor.SaveImage128SaveImage(self)  # noqa
        self._save_image_01: FluxNegUpscaleSdxl0Dot4Accessor.SaveImage129SaveImage = FluxNegUpscaleSdxl0Dot4Accessor.SaveImage129SaveImage(self)  # noqa

    @property
    def positive_prompt(self):
        return self._positive_prompt

    @positive_prompt.setter
    def positive_prompt(self, value):
        self._positive_prompt = value

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
    def tobasicpipe(self):
        return self._tobasicpipe

    @tobasicpipe.setter
    def tobasicpipe(self, value):
        self._tobasicpipe = value

    @property
    def empty_latent_image(self):
        return self._empty_latent_image

    @empty_latent_image.setter
    def empty_latent_image(self, value):
        self._empty_latent_image = value

    @property
    def ksampler_pass2_advancedpipe(self):
        return self._ksampler_pass2_advancedpipe

    @ksampler_pass2_advancedpipe.setter
    def ksampler_pass2_advancedpipe(self, value):
        self._ksampler_pass2_advancedpipe = value

    @property
    def ksampler_pass1_advancedpipe(self):
        return self._ksampler_pass1_advancedpipe

    @ksampler_pass1_advancedpipe.setter
    def ksampler_pass1_advancedpipe(self, value):
        self._ksampler_pass1_advancedpipe = value

    @property
    def dynamicthresholdingfull(self):
        return self._dynamicthresholdingfull

    @dynamicthresholdingfull.setter
    def dynamicthresholdingfull(self, value):
        self._dynamicthresholdingfull = value

    @property
    def negative_prompt(self):
        return self._negative_prompt

    @negative_prompt.setter
    def negative_prompt(self, value):
        self._negative_prompt = value

    @property
    def edit_basicpipe(self):
        return self._edit_basicpipe

    @edit_basicpipe.setter
    def edit_basicpipe(self, value):
        self._edit_basicpipe = value

    @property
    def frombasicpipe_v2(self):
        return self._frombasicpipe_v2

    @frombasicpipe_v2.setter
    def frombasicpipe_v2(self, value):
        self._frombasicpipe_v2 = value

    @property
    def negative_cond_placeholder(self):
        return self._negative_cond_placeholder

    @negative_cond_placeholder.setter
    def negative_cond_placeholder(self, value):
        self._negative_cond_placeholder = value

    @property
    def vae_decode(self):
        return self._vae_decode

    @vae_decode.setter
    def vae_decode(self, value):
        self._vae_decode = value

    @property
    def sd_4xupscale_conditioning(self):
        return self._sd_4xupscale_conditioning

    @sd_4xupscale_conditioning.setter
    def sd_4xupscale_conditioning(self, value):
        self._sd_4xupscale_conditioning = value

    @property
    def efficient_loader(self):
        return self._efficient_loader

    @efficient_loader.setter
    def efficient_loader(self, value):
        self._efficient_loader = value

    @property
    def ultimate_sd_upscale(self):
        return self._ultimate_sd_upscale

    @ultimate_sd_upscale.setter
    def ultimate_sd_upscale(self, value):
        self._ultimate_sd_upscale = value

    @property
    def load_upscale_model(self):
        return self._load_upscale_model

    @load_upscale_model.setter
    def load_upscale_model(self, value):
        self._load_upscale_model = value

    @property
    def get_image_size__count(self):
        return self._get_image_size__count

    @get_image_size__count.setter
    def get_image_size__count(self, value):
        self._get_image_size__count = value

    @property
    def save_image(self):
        return self._save_image

    @save_image.setter
    def save_image(self, value):
        self._save_image = value

    @property
    def save_image_01(self):
        return self._save_image_01

    @save_image_01.setter
    def save_image_01(self, value):
        self._save_image_01 = value
