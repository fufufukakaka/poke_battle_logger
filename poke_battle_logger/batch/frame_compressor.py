FRAME_SEQUENCE_THRESHOLD = 100


def frame_compress(target_frames):
    # フレームを連続区間で分割する
    compressed_frame_results = []
    temp = []
    for i in range(len(target_frames)):
        temp.append(target_frames[i])
        if (
            i < len(target_frames) - 1
            and target_frames[i + 1] - target_frames[i] > FRAME_SEQUENCE_THRESHOLD
        ):
            compressed_frame_results.append(temp)
            temp = []
    compressed_frame_results.append(temp)
    return compressed_frame_results
