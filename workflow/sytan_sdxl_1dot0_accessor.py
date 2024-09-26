from enum import Enum
from workflow.node_accessor import NodesAccessor


class SytanSdxl1Dot0Accessor(NodesAccessor):
    WORKFLOW_FILE = "sytan_sdxl_1.0_workflow_api.json"

    class NodeIndexes(Enum):
        NODE_REFINER_MODEL = "4"
        NODE_IMAGE_RESOLUTION = "5"
        NODE_VAE_DECODE = "8"
        NODE_BASE_MODEL = "10"
        NODE_BASE_PASS = "22"
        NODE_REFINER_PASS = "23"
        NODE_POSITIVE_BASE = "75"
        NODE_NEGATIVE_REFINER = "81"
        NODE_NEGATIVE_BASE = "82"
        NODE_POSITIVE_REFINER = "120"
        NODE_SYTAN_WORKFLOW = "184"
        NODE_UPSCALE_MODEL = "187"
        NODE_2048X_UPSCALE = "201"
        NODE_PIXEL_UPSCALE_X4 = "213"
        NODE_DOWNSCALE = "215"
        NODE_UPSCALE_MIXED_DIFF = "216"
        NODE_VAE_ENCODE = "217"
        NODE_VAE_DECODE_01 = "218"
        NODE_CONTRAST_FIX = "221"

    class CheckpointLoaderSimple004RefinerModel:

        def __init__(self, outer):
            self._outer = outer

        @property
        def ckpt_name(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_MODEL.value]["inputs"]["ckpt_name"]  # noqa

        @ckpt_name.setter
        def ckpt_name(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_MODEL.value]["inputs"]["ckpt_name"] = value  # noqa

    class EmptyLatentImage005ImageResolution:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_IMAGE_RESOLUTION.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_IMAGE_RESOLUTION.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_IMAGE_RESOLUTION.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_IMAGE_RESOLUTION.value]["inputs"]["height"] = value  # noqa

        @property
        def batch_size(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_IMAGE_RESOLUTION.value]["inputs"]["batch_size"]  # noqa

        @batch_size.setter
        def batch_size(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_IMAGE_RESOLUTION.value]["inputs"]["batch_size"] = value  # noqa

    class VAEDecode008VaeDecode:

        def __init__(self, outer):
            self._outer = outer

    class CheckpointLoaderSimple010BaseModel:

        def __init__(self, outer):
            self._outer = outer

        @property
        def ckpt_name(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_MODEL.value]["inputs"]["ckpt_name"]  # noqa

        @ckpt_name.setter
        def ckpt_name(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_MODEL.value]["inputs"]["ckpt_name"] = value  # noqa

    class KSamplerAdvanced022BasePass:

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_BASE_PASS.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class KSamplerAdvanced023RefinerPass:

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_REFINER_PASS.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class CLIPTextEncodeSDXL075PositiveBase:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["height"] = value  # noqa

        @property
        def crop_w(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["crop_w"]  # noqa

        @crop_w.setter
        def crop_w(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["crop_w"] = value  # noqa

        @property
        def crop_h(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["crop_h"]  # noqa

        @crop_h.setter
        def crop_h(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["crop_h"] = value  # noqa

        @property
        def target_width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["target_width"]  # noqa

        @target_width.setter
        def target_width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["target_width"] = value  # noqa

        @property
        def target_height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["target_height"]  # noqa

        @target_height.setter
        def target_height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["target_height"] = value  # noqa

        @property
        def text_g(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["text_g"]  # noqa

        @text_g.setter
        def text_g(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["text_g"] = value  # noqa

        @property
        def text_l(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["text_l"]  # noqa

        @text_l.setter
        def text_l(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_BASE.value]["inputs"]["text_l"] = value  # noqa

    class CLIPTextEncodeSDXLRefiner081NegativeRefiner:

        def __init__(self, outer):
            self._outer = outer

        @property
        def ascore(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["ascore"]  # noqa

        @ascore.setter
        def ascore(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["ascore"] = value  # noqa

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["height"] = value  # noqa

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_REFINER.value]["inputs"]["text"] = value  # noqa

    class CLIPTextEncodeSDXL082NegativeBase:

        def __init__(self, outer):
            self._outer = outer

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["height"] = value  # noqa

        @property
        def crop_w(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["crop_w"]  # noqa

        @crop_w.setter
        def crop_w(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["crop_w"] = value  # noqa

        @property
        def crop_h(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["crop_h"]  # noqa

        @crop_h.setter
        def crop_h(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["crop_h"] = value  # noqa

        @property
        def target_width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["target_width"]  # noqa

        @target_width.setter
        def target_width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["target_width"] = value  # noqa

        @property
        def target_height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["target_height"]  # noqa

        @target_height.setter
        def target_height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["target_height"] = value  # noqa

        @property
        def text_g(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["text_g"]  # noqa

        @text_g.setter
        def text_g(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["text_g"] = value  # noqa

        @property
        def text_l(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["text_l"]  # noqa

        @text_l.setter
        def text_l(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_NEGATIVE_BASE.value]["inputs"]["text_l"] = value  # noqa

    class CLIPTextEncodeSDXLRefiner120PositiveRefiner:

        def __init__(self, outer):
            self._outer = outer

        @property
        def ascore(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["ascore"]  # noqa

        @ascore.setter
        def ascore(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["ascore"] = value  # noqa

        @property
        def width(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["width"]  # noqa

        @width.setter
        def width(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["width"] = value  # noqa

        @property
        def height(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["height"]  # noqa

        @height.setter
        def height(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["height"] = value  # noqa

        @property
        def text(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["text"]  # noqa

        @text.setter
        def text(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_POSITIVE_REFINER.value]["inputs"]["text"] = value  # noqa

    class SaveImage184SytanWorkflow:

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_SYTAN_WORKFLOW.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_SYTAN_WORKFLOW.value]["inputs"]["filename_prefix"] = value  # noqa

    class UpscaleModelLoader187UpscaleModel:

        def __init__(self, outer):
            self._outer = outer

        @property
        def model_name(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MODEL.value]["inputs"]["model_name"]  # noqa

        @model_name.setter
        def model_name(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MODEL.value]["inputs"]["model_name"] = value  # noqa

    class SaveImage2012048XUpscale:

        def __init__(self, outer):
            self._outer = outer

        @property
        def filename_prefix(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_2048X_UPSCALE.value]["inputs"]["filename_prefix"]  # noqa

        @filename_prefix.setter
        def filename_prefix(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_2048X_UPSCALE.value]["inputs"]["filename_prefix"] = value  # noqa

    class ImageUpscaleWithModel213PixelUpscaleX4:

        def __init__(self, outer):
            self._outer = outer

    class ImageScaleBy215Downscale:

        def __init__(self, outer):
            self._outer = outer

        @property
        def upscale_method(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_DOWNSCALE.value]["inputs"]["upscale_method"]  # noqa

        @upscale_method.setter
        def upscale_method(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_DOWNSCALE.value]["inputs"]["upscale_method"] = value  # noqa

        @property
        def scale_by(self) -> float:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_DOWNSCALE.value]["inputs"]["scale_by"]  # noqa

        @scale_by.setter
        def scale_by(self, value: float):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_DOWNSCALE.value]["inputs"]["scale_by"] = value  # noqa

    class KSamplerAdvanced216UpscaleMixedDiff:

        def __init__(self, outer):
            self._outer = outer

        @property
        def add_noise(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["add_noise"]  # noqa

        @add_noise.setter
        def add_noise(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["add_noise"] = value  # noqa

        @property
        def noise_seed(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["noise_seed"]  # noqa

        @noise_seed.setter
        def noise_seed(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["noise_seed"] = value  # noqa

        @property
        def steps(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["steps"]  # noqa

        @steps.setter
        def steps(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["steps"] = value  # noqa

        @property
        def cfg(self) -> float:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["cfg"]  # noqa

        @cfg.setter
        def cfg(self, value: float):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["cfg"] = value  # noqa

        @property
        def sampler_name(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["sampler_name"]  # noqa

        @sampler_name.setter
        def sampler_name(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["sampler_name"] = value  # noqa

        @property
        def scheduler(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["scheduler"]  # noqa

        @scheduler.setter
        def scheduler(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["scheduler"] = value  # noqa

        @property
        def start_at_step(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["start_at_step"]  # noqa

        @start_at_step.setter
        def start_at_step(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["start_at_step"] = value  # noqa

        @property
        def end_at_step(self) -> int:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["end_at_step"]  # noqa

        @end_at_step.setter
        def end_at_step(self, value: int):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["end_at_step"] = value  # noqa

        @property
        def return_with_leftover_noise(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["return_with_leftover_noise"]  # noqa

        @return_with_leftover_noise.setter
        def return_with_leftover_noise(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_UPSCALE_MIXED_DIFF.value]["inputs"]["return_with_leftover_noise"] = value  # noqa

    class VAEEncode217VaeEncode:

        def __init__(self, outer):
            self._outer = outer

    class VAEDecode218VaeDecode:

        def __init__(self, outer):
            self._outer = outer

    class ImageBlend221ContrastFix:

        def __init__(self, outer):
            self._outer = outer

        @property
        def blend_factor(self) -> float:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_CONTRAST_FIX.value]["inputs"]["blend_factor"]  # noqa

        @blend_factor.setter
        def blend_factor(self, value: float):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_CONTRAST_FIX.value]["inputs"]["blend_factor"] = value  # noqa

        @property
        def blend_mode(self) -> str:
            return self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_CONTRAST_FIX.value]["inputs"]["blend_mode"]  # noqa

        @blend_mode.setter
        def blend_mode(self, value: str):
            self._outer.nodes_dict[SytanSdxl1Dot0Accessor.NodeIndexes.NODE_CONTRAST_FIX.value]["inputs"]["blend_mode"] = value  # noqa

    def __init__(self):
        super().__init__(SytanSdxl1Dot0Accessor.WORKFLOW_FILE)
        self._refiner_model: SytanSdxl1Dot0Accessor.CheckpointLoaderSimple004RefinerModel = SytanSdxl1Dot0Accessor.CheckpointLoaderSimple004RefinerModel(self)  # noqa
        self._image_resolution: SytanSdxl1Dot0Accessor.EmptyLatentImage005ImageResolution = SytanSdxl1Dot0Accessor.EmptyLatentImage005ImageResolution(self)  # noqa
        self._vae_decode: SytanSdxl1Dot0Accessor.VAEDecode008VaeDecode = SytanSdxl1Dot0Accessor.VAEDecode008VaeDecode(self)  # noqa
        self._base_model: SytanSdxl1Dot0Accessor.CheckpointLoaderSimple010BaseModel = SytanSdxl1Dot0Accessor.CheckpointLoaderSimple010BaseModel(self)  # noqa
        self._base_pass: SytanSdxl1Dot0Accessor.KSamplerAdvanced022BasePass = SytanSdxl1Dot0Accessor.KSamplerAdvanced022BasePass(self)  # noqa
        self._refiner_pass: SytanSdxl1Dot0Accessor.KSamplerAdvanced023RefinerPass = SytanSdxl1Dot0Accessor.KSamplerAdvanced023RefinerPass(self)  # noqa
        self._positive_base: SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXL075PositiveBase = SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXL075PositiveBase(self)  # noqa
        self._negative_refiner: SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXLRefiner081NegativeRefiner = SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXLRefiner081NegativeRefiner(self)  # noqa
        self._negative_base: SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXL082NegativeBase = SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXL082NegativeBase(self)  # noqa
        self._positive_refiner: SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXLRefiner120PositiveRefiner = SytanSdxl1Dot0Accessor.CLIPTextEncodeSDXLRefiner120PositiveRefiner(self)  # noqa
        self._sytan_workflow: SytanSdxl1Dot0Accessor.SaveImage184SytanWorkflow = SytanSdxl1Dot0Accessor.SaveImage184SytanWorkflow(self)  # noqa
        self._upscale_model: SytanSdxl1Dot0Accessor.UpscaleModelLoader187UpscaleModel = SytanSdxl1Dot0Accessor.UpscaleModelLoader187UpscaleModel(self)  # noqa
        self._zz2048x_upscale: SytanSdxl1Dot0Accessor.SaveImage2012048XUpscale = SytanSdxl1Dot0Accessor.SaveImage2012048XUpscale(self)  # noqa
        self._pixel_upscale_x4: SytanSdxl1Dot0Accessor.ImageUpscaleWithModel213PixelUpscaleX4 = SytanSdxl1Dot0Accessor.ImageUpscaleWithModel213PixelUpscaleX4(self)  # noqa
        self._downscale: SytanSdxl1Dot0Accessor.ImageScaleBy215Downscale = SytanSdxl1Dot0Accessor.ImageScaleBy215Downscale(self)  # noqa
        self._upscale_mixed_diff: SytanSdxl1Dot0Accessor.KSamplerAdvanced216UpscaleMixedDiff = SytanSdxl1Dot0Accessor.KSamplerAdvanced216UpscaleMixedDiff(self)  # noqa
        self._vae_encode: SytanSdxl1Dot0Accessor.VAEEncode217VaeEncode = SytanSdxl1Dot0Accessor.VAEEncode217VaeEncode(self)  # noqa
        self._vae_decode_01: SytanSdxl1Dot0Accessor.VAEDecode218VaeDecode = SytanSdxl1Dot0Accessor.VAEDecode218VaeDecode(self)  # noqa
        self._contrast_fix: SytanSdxl1Dot0Accessor.ImageBlend221ContrastFix = SytanSdxl1Dot0Accessor.ImageBlend221ContrastFix(self)  # noqa

    @property
    def refiner_model(self):
        return self._refiner_model

    @refiner_model.setter
    def refiner_model(self, value):
        self._refiner_model = value

    @property
    def image_resolution(self):
        return self._image_resolution

    @image_resolution.setter
    def image_resolution(self, value):
        self._image_resolution = value

    @property
    def vae_decode(self):
        return self._vae_decode

    @vae_decode.setter
    def vae_decode(self, value):
        self._vae_decode = value

    @property
    def base_model(self):
        return self._base_model

    @base_model.setter
    def base_model(self, value):
        self._base_model = value

    @property
    def base_pass(self):
        return self._base_pass

    @base_pass.setter
    def base_pass(self, value):
        self._base_pass = value

    @property
    def refiner_pass(self):
        return self._refiner_pass

    @refiner_pass.setter
    def refiner_pass(self, value):
        self._refiner_pass = value

    @property
    def positive_base(self):
        return self._positive_base

    @positive_base.setter
    def positive_base(self, value):
        self._positive_base = value

    @property
    def negative_refiner(self):
        return self._negative_refiner

    @negative_refiner.setter
    def negative_refiner(self, value):
        self._negative_refiner = value

    @property
    def negative_base(self):
        return self._negative_base

    @negative_base.setter
    def negative_base(self, value):
        self._negative_base = value

    @property
    def positive_refiner(self):
        return self._positive_refiner

    @positive_refiner.setter
    def positive_refiner(self, value):
        self._positive_refiner = value

    @property
    def sytan_workflow(self):
        return self._sytan_workflow

    @sytan_workflow.setter
    def sytan_workflow(self, value):
        self._sytan_workflow = value

    @property
    def upscale_model(self):
        return self._upscale_model

    @upscale_model.setter
    def upscale_model(self, value):
        self._upscale_model = value

    @property
    def zz2048x_upscale(self):
        return self._zz2048x_upscale

    @zz2048x_upscale.setter
    def zz2048x_upscale(self, value):
        self._zz2048x_upscale = value

    @property
    def pixel_upscale_x4(self):
        return self._pixel_upscale_x4

    @pixel_upscale_x4.setter
    def pixel_upscale_x4(self, value):
        self._pixel_upscale_x4 = value

    @property
    def downscale(self):
        return self._downscale

    @downscale.setter
    def downscale(self, value):
        self._downscale = value

    @property
    def upscale_mixed_diff(self):
        return self._upscale_mixed_diff

    @upscale_mixed_diff.setter
    def upscale_mixed_diff(self, value):
        self._upscale_mixed_diff = value

    @property
    def vae_encode(self):
        return self._vae_encode

    @vae_encode.setter
    def vae_encode(self, value):
        self._vae_encode = value

    @property
    def vae_decode_01(self):
        return self._vae_decode_01

    @vae_decode_01.setter
    def vae_decode_01(self, value):
        self._vae_decode_01 = value

    @property
    def contrast_fix(self):
        return self._contrast_fix

    @contrast_fix.setter
    def contrast_fix(self, value):
        self._contrast_fix = value
