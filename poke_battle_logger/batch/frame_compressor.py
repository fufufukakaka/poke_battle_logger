FRAME_SEQUENCE_THRESHOLD = 100


def frame_compress(target_frames, frame_threshold=FRAME_SEQUENCE_THRESHOLD):
    # フレームを連続区間で分割する
    compressed_frame_results = []
    temp = []
    for i in range(len(target_frames)):
        temp.append(target_frames[i])
        if (
            i < len(target_frames) - 1
            and target_frames[i + 1] - target_frames[i] > frame_threshold
        ):
            compressed_frame_results.append(temp)
            temp = []
    compressed_frame_results.append(temp)
    return compressed_frame_results


def message_frame_compress(target_frames, frame_threshold=3):
    # フレームを連続区間で分割する
    message_frame_results = []
    temp2 = []
    for i in range(len(target_frames)):
        temp2.append(target_frames[i])
        if i < len(target_frames)-1 and target_frames[i+1] - target_frames[i] > frame_threshold:
            if len(temp2) > 1:
                message_frame_results.append(temp2)
            temp2 = []
    message_frame_results.append(temp2)
    return message_frame_results
