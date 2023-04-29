from typing import List

FRAME_SEQUENCE_THRESHOLD = 100


def frame_compress(
    target_frames: List[int],
    frame_threshold: int = FRAME_SEQUENCE_THRESHOLD,
    ignore_short_frames: bool = False,
) -> List[List[int]]:
    # フレームを連続区間で分割する
    compressed_frame_results: List[List[int]] = []
    temp = []
    for i in range(len(target_frames)):
        temp.append(target_frames[i])
        if (
            i < len(target_frames) - 1
            and target_frames[i + 1] - target_frames[i] > frame_threshold
        ):
            if ignore_short_frames:
                if len(temp) > 1:
                    compressed_frame_results.append(temp)
                else:
                    pass
            else:
                compressed_frame_results.append(temp)
            temp = []
    return compressed_frame_results


def message_frame_compress(
    target_frames: List[int], frame_threshold: int = 3
) -> List[List[int]]:
    # フレームを連続区間で分割する
    message_frame_results = []
    temp2 = []
    for i in range(len(target_frames)):
        temp2.append(target_frames[i])
        if (
            i < len(target_frames) - 1
            and target_frames[i + 1] - target_frames[i] > frame_threshold
        ):
            if len(temp2) > 1:
                message_frame_results.append(temp2)
            temp2 = []
    message_frame_results.append(temp2)
    return message_frame_results
