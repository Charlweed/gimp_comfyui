from enum import Enum
from workflow.node_accessor import NodesAccessor


class FluxNeg1Dot0Accessor(NodesAccessor):
    WORKFLOW_FILE = "flux_neg_1.0_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_CLIP_TEXT_ENCODE_PROMPT = "6"
        NODE_LOAD_VAE = "10"
        NODE_DUALCLIPLOADER = "11"
        NODE_LOAD_DIFFUSION_MODEL = "12"
        NODE_TOBASICPIPE = "47"
        NODE_PREVIEW_BRIDGE_LATENT = "48"
        NODE_EMPTY_LATENT_IMAGE = "49"
        NODE_KSAMPLER_ADVANCEDPIPE = "97"
        NODE_KSAMPLER_ADVANCEDPIPE_01 = "98"
        NODE_DYNAMICTHRESHOLDINGFULL = "100"
        NODE_CLIP_TEXT_ENCODE_PROMPT_01 = "101"
        NODE_EDIT_BASICPIPE = "103"
        NODE_FROMBASICPIPE_V2 = "104"
        NODE_NEGATIVE_COND_PLACEHOLDER = "105"

    class CLIPTextEncode006ClipTextEncodePrompt:

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_CLIP_TEXT_ENCODE_PROMPT.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_CLIP_TEXT_ENCODE_PROMPT.value]["inputs"]["text"] = value  # noqa

    class VAELoader010LoadVae:

        def __init__(self, outer):
            self._outer = outer

        @property
        def vae_name(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"]  # noqa

        @vae_name.setter
        def vae_name(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_LOAD_VAE.value]["inputs"]["vae_name"] = value  # noqa

    class DualCLIPLoader011Dualcliploader:

        def __init__(self, outer):
            self._outer = outer

        @property
        def clip_name1(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name1"]  # noqa

        @clip_name1.setter
        def clip_name1(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name1"] = value  # noqa

        @property
        def clip_name2(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name2"]  # noqa

        @clip_name2.setter
        def clip_name2(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["clip_name2"] = value  # noqa

        @property
        def type(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["type"]  # noqa

        @type.setter
        def type(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DUALCLIPLOADER.value]["inputs"]["type"] = value  # noqa

    class UNETLoader012LoadDiffusionModel:

        def __init__(self, outer):
            self._outer = outer

        @property
        def unet_name(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"]  # noqa

        @unet_name.setter
        def unet_name(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["unet_name"] = value  # noqa

        @property
        def weight_dtype(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"]  # noqa

        @weight_dtype.setter
        def weight_dtype(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_LOAD_DIFFUSION_MODEL.value]["inputs"]["weight_dtype"] = value  # noqa

    class ToBasicPipe047Tobasicpipe:

        def __init__(self, outer):
            self._outer = outer

    class PreviewBridgeLatent048PreviewBridgeLatent:

        def __init__(self, outer):
            self._outer = outer

        @property
        def image(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_PREVIEW_BRIDGE_LATENT.value]["inputs"]["image"]  # noqa

        @image.setter
        def image(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_PREVIEW_BRIDGE_LATENT.value]["inputs"]["image"] = value  # noqa

        @property
        def preview_method(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_PREVIEW_BRIDGE_LATENT.value]["inputs"]["preview_method"]  # noqa

        @preview_method.setter
        def preview_method(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_PREVIEW_BRIDGE_LATENT.value]["inputs"]["preview_method"] = value  # noqa

        @property
        def block(self) -> bool:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_PREVIEW_BRIDGE_LATENT.value]["inputs"]["block"]  # noqa

        @block.setter
        def block(self, value: bool):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_PREVIEW_BRIDGE_LATENT.value]["inputs"]["block"] = value  # noqa

    class EmptyLatentImage049EmptyLatentImage:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["height"] = value  # noqa

        @property
        def batch_size(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["batch_size"]  # noqa

        @batch_size.setter
        def batch_size(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_EMPTY_LATENT_IMAGE.value]["inputs"]["batch_size"] = value  # noqa

    class ImpactKSamplerAdvancedBasicPipe097KsamplerAdvancedpipe:

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: bool):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: bool):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class ImpactKSamplerAdvancedBasicPipe098KsamplerAdvancedpipe:

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: bool):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> bool:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: bool):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_KSAMPLER_ADVANCEDPIPE_01.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class DynamicThresholdingFull100Dynamicthresholdingfull:

        def __init__(self, outer):
            self._outer = outer

        @property
        def mimic_scale(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale"]  # noqa

        @mimic_scale.setter
        def mimic_scale(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale"] = value  # noqa

        @property
        def threshold_percentile(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["threshold_percentile"]  # noqa

        @threshold_percentile.setter
        def threshold_percentile(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["threshold_percentile"] = value  # noqa

        @property
        def mimic_mode(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_mode"]  # noqa

        @mimic_mode.setter
        def mimic_mode(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_mode"] = value  # noqa

        @property
        def mimic_scale_min(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale_min"]  # noqa

        @mimic_scale_min.setter
        def mimic_scale_min(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["mimic_scale_min"] = value  # noqa

        @property
        def cfg_mode(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_mode"]  # noqa

        @cfg_mode.setter
        def cfg_mode(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_mode"] = value  # noqa

        @property
        def cfg_scale_min(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_scale_min"]  # noqa

        @cfg_scale_min.setter
        def cfg_scale_min(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["cfg_scale_min"] = value  # noqa

        @property
        def sched_val(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["sched_val"]  # noqa

        @sched_val.setter
        def sched_val(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["sched_val"] = value  # noqa

        @property
        def separate_feature_channels(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["separate_feature_channels"]  # noqa

        @separate_feature_channels.setter
        def separate_feature_channels(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["separate_feature_channels"] = value  # noqa

        @property
        def scaling_startpoint(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["scaling_startpoint"]  # noqa

        @scaling_startpoint.setter
        def scaling_startpoint(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["scaling_startpoint"] = value  # noqa

        @property
        def variability_measure(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["variability_measure"]  # noqa

        @variability_measure.setter
        def variability_measure(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["variability_measure"] = value  # noqa

        @property
        def interpolate_phi(self) -> int:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["interpolate_phi"]  # noqa

        @interpolate_phi.setter
        def interpolate_phi(self, value: int):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_DYNAMICTHRESHOLDINGFULL.value]["inputs"]["interpolate_phi"] = value  # noqa

    class CLIPTextEncode101ClipTextEncodePrompt:

        def __init__(self, outer):
            self._outer = outer

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_CLIP_TEXT_ENCODE_PROMPT_01.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[FluxNeg1Dot0Accessor.NodeIndexes.NODE_CLIP_TEXT_ENCODE_PROMPT_01.value]["inputs"]["text"] = value  # noqa

    class EditBasicPipe103EditBasicpipe:

        def __init__(self, outer):
            self._outer = outer

    class FromBasicPipe_v2104FrombasicpipeV2:

        def __init__(self, outer):
            self._outer = outer

    class ImpactNegativeConditioningPlaceholder105NegativeCondPlaceholder:

        def __init__(self, outer):
            self._outer = outer

    def __init__(self):
        super().__init__(FluxNeg1Dot0Accessor.WORKFLOW_FILE)
        self._clip_text_encode_prompt: FluxNeg1Dot0Accessor.CLIPTextEncode006ClipTextEncodePrompt = FluxNeg1Dot0Accessor.CLIPTextEncode006ClipTextEncodePrompt(self)  # noqa
        self._load_vae: FluxNeg1Dot0Accessor.VAELoader010LoadVae = FluxNeg1Dot0Accessor.VAELoader010LoadVae(self)  # noqa
        self._dualcliploader: FluxNeg1Dot0Accessor.DualCLIPLoader011Dualcliploader = FluxNeg1Dot0Accessor.DualCLIPLoader011Dualcliploader(self)  # noqa
        self._load_diffusion_model: FluxNeg1Dot0Accessor.UNETLoader012LoadDiffusionModel = FluxNeg1Dot0Accessor.UNETLoader012LoadDiffusionModel(self)  # noqa
        self._tobasicpipe: FluxNeg1Dot0Accessor.ToBasicPipe047Tobasicpipe = FluxNeg1Dot0Accessor.ToBasicPipe047Tobasicpipe(self)  # noqa
        self._preview_bridge_latent: FluxNeg1Dot0Accessor.PreviewBridgeLatent048PreviewBridgeLatent = FluxNeg1Dot0Accessor.PreviewBridgeLatent048PreviewBridgeLatent(self)  # noqa
        self._empty_latent_image: FluxNeg1Dot0Accessor.EmptyLatentImage049EmptyLatentImage = FluxNeg1Dot0Accessor.EmptyLatentImage049EmptyLatentImage(self)  # noqa
        self._ksampler_advancedpipe: FluxNeg1Dot0Accessor.ImpactKSamplerAdvancedBasicPipe097KsamplerAdvancedpipe = FluxNeg1Dot0Accessor.ImpactKSamplerAdvancedBasicPipe097KsamplerAdvancedpipe(self)  # noqa
        self._ksampler_advancedpipe_01: FluxNeg1Dot0Accessor.ImpactKSamplerAdvancedBasicPipe098KsamplerAdvancedpipe = FluxNeg1Dot0Accessor.ImpactKSamplerAdvancedBasicPipe098KsamplerAdvancedpipe(self)  # noqa
        self._dynamicthresholdingfull: FluxNeg1Dot0Accessor.DynamicThresholdingFull100Dynamicthresholdingfull = FluxNeg1Dot0Accessor.DynamicThresholdingFull100Dynamicthresholdingfull(self)  # noqa
        self._clip_text_encode_prompt_01: FluxNeg1Dot0Accessor.CLIPTextEncode101ClipTextEncodePrompt = FluxNeg1Dot0Accessor.CLIPTextEncode101ClipTextEncodePrompt(self)  # noqa
        self._edit_basicpipe: FluxNeg1Dot0Accessor.EditBasicPipe103EditBasicpipe = FluxNeg1Dot0Accessor.EditBasicPipe103EditBasicpipe(self)  # noqa
        self._frombasicpipe_v2: FluxNeg1Dot0Accessor.FromBasicPipe_v2104FrombasicpipeV2 = FluxNeg1Dot0Accessor.FromBasicPipe_v2104FrombasicpipeV2(self)  # noqa
        self._negative_cond_placeholder: FluxNeg1Dot0Accessor.ImpactNegativeConditioningPlaceholder105NegativeCondPlaceholder = FluxNeg1Dot0Accessor.ImpactNegativeConditioningPlaceholder105NegativeCondPlaceholder(self)  # noqa

    @property
    def clip_text_encode_prompt(self):
        return self._clip_text_encode_prompt

    @clip_text_encode_prompt.setter
    def clip_text_encode_prompt(self, value):
        self._clip_text_encode_prompt = value

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
    def preview_bridge_latent(self):
        return self._preview_bridge_latent

    @preview_bridge_latent.setter
    def preview_bridge_latent(self, value):
        self._preview_bridge_latent = value

    @property
    def empty_latent_image(self):
        return self._empty_latent_image

    @empty_latent_image.setter
    def empty_latent_image(self, value):
        self._empty_latent_image = value

    @property
    def ksampler_advancedpipe(self):
        return self._ksampler_advancedpipe

    @ksampler_advancedpipe.setter
    def ksampler_advancedpipe(self, value):
        self._ksampler_advancedpipe = value

    @property
    def ksampler_advancedpipe_01(self):
        return self._ksampler_advancedpipe_01

    @ksampler_advancedpipe_01.setter
    def ksampler_advancedpipe_01(self, value):
        self._ksampler_advancedpipe_01 = value

    @property
    def dynamicthresholdingfull(self):
        return self._dynamicthresholdingfull

    @dynamicthresholdingfull.setter
    def dynamicthresholdingfull(self, value):
        self._dynamicthresholdingfull = value

    @property
    def clip_text_encode_prompt_01(self):
        return self._clip_text_encode_prompt_01

    @clip_text_encode_prompt_01.setter
    def clip_text_encode_prompt_01(self, value):
        self._clip_text_encode_prompt_01 = value

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
