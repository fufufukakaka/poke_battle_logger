import os
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from poke_battle_logger.batch.extractor import Extractor

# Import from local modules
from poke_battle_logger.batch.frame_detector import FrameDetector

st.set_page_config(page_title="Frame Detector Debugger", layout="wide")


def load_video_files():
    """Load available video files from video directory."""
    video_dir = Path("video")
    if not video_dir.exists():
        video_dir.mkdir(exist_ok=True)
        return []

    video_files = []
    for ext in [".mp4", ".avi", ".mov", ".mkv"]:
        video_files.extend(list(video_dir.glob(f"*{ext}")))

    return [f.name for f in video_files]


def get_frame_from_video(video_path, frame_number):
    """Extract specific frame from video."""
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_number >= total_frames:
        cap.release()
        return None, total_frames

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame, total_frames
    return None, total_frames


def test_frame_detector_methods(frame, frame_detector):
    """Test all FrameDetector methods on the given frame."""
    results = {}

    methods_to_test = [
        ("is_message_window_frame", "Message Window"),
        ("is_level_50_frame", "Level 50"),
        ("is_first_ranking_frame", "First Ranking"),
        ("is_select_done_frame", "Select Done"),
        ("is_standing_by_frame", "Standing By"),
        ("is_ranking_frame", "Ranking"),
        ("is_win_or_lost_frame", "Win/Lost"),
        ("is_move_frame", "Move"),
        ("is_pokemon_selection_frame", "Pokemon Selection"),
    ]

    for method_name, display_name in methods_to_test:
        try:
            method = getattr(frame_detector, method_name)
            result = method(frame)
            results[display_name] = result
        except Exception as e:
            results[display_name] = f"Error: {str(e)}"

    return results


def draw_detection_regions(frame):
    """Draw detection regions on frame for visualization."""
    frame_copy = frame.copy()

    # Import config constants
    from config.config import (
        FIRST_RANKING_WINDOW,
        LEVEL_50_WINDOW,
        MOVE_ANKER_POSITION,
        MOVE_SELECT_WINDOW1,
        MOVE_SELECT_WINDOW2,
        MOVE_SELECT_WINDOW3,
        MOVE_SELECT_WINDOW4,
        MOVE_TITLE1,
        MOVE_TITLE2,
        MOVE_TITLE3,
        MOVE_TITLE4,
        POKEMON_MESSAGE_WINDOW,
        POKEMON_SELECT_DONE_WINDOW,
        POKEMON_SELECTION_ICON,
        RANKING_WINDOW,
        STANDING_BY_WINDOW,
        WIN_LOST_WINDOW,
    )

    regions = [
        (STANDING_BY_WINDOW, (0, 255, 0), "Standing By"),
        (LEVEL_50_WINDOW, (255, 0, 0), "Level 50"),
        (FIRST_RANKING_WINDOW, (255, 255, 0), "First Ranking"),
        (RANKING_WINDOW, (0, 255, 255), "Ranking"),
        (WIN_LOST_WINDOW, (255, 0, 255), "Win/Lost"),
        (POKEMON_SELECT_DONE_WINDOW, (128, 255, 128), "Select Done"),
        (POKEMON_MESSAGE_WINDOW, (255, 128, 0), "Message"),
        (MOVE_ANKER_POSITION, (128, 128, 255), "Move Anchor"),
        (POKEMON_SELECTION_ICON, (255, 255, 128), "Pokemon Selection"),
        (MOVE_SELECT_WINDOW1, (255, 192, 203), "Move Select 1"),
        (MOVE_SELECT_WINDOW2, (255, 192, 203), "Move Select 2"),
        (MOVE_SELECT_WINDOW3, (255, 192, 203), "Move Select 3"),
        (MOVE_SELECT_WINDOW4, (255, 192, 203), "Move Select 4"),
        (MOVE_TITLE1, (173, 216, 230), "Move Title 1"),
        (MOVE_TITLE2, (173, 216, 230), "Move Title 2"),
        (MOVE_TITLE3, (173, 216, 230), "Move Title 3"),
        (MOVE_TITLE4, (173, 216, 230), "Move Title 4"),
    ]

    for window, color, label in regions:
        y1, y2, x1, x2 = window
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame_copy, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
        )

    return frame_copy


def debug_is_move_frame(frame, frame_detector):
    """Debug is_move_frame method step by step."""
    from config.config import MOVE_ANKER_POSITION, MOVE_ANKER_THRESHOLD
    
    # Extract the move anchor area
    gray_move_anker_area = cv2.cvtColor(
        frame[
            MOVE_ANKER_POSITION[0] : MOVE_ANKER_POSITION[1],
            MOVE_ANKER_POSITION[2] : MOVE_ANKER_POSITION[3],
        ],
        cv2.COLOR_BGR2GRAY,
    )
    
    # Perform template matching
    result = cv2.matchTemplate(
        gray_move_anker_area, frame_detector.gray_move_anker_template, cv2.TM_CCOEFF_NORMED
    )
    
    # Get matching result details
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    is_move_frame_result = max_val >= MOVE_ANKER_THRESHOLD
    
    return {
        "move_anker_position": MOVE_ANKER_POSITION,
        "move_anker_threshold": MOVE_ANKER_THRESHOLD,
        "gray_move_anker_area": gray_move_anker_area,
        "template_match_result": result,
        "min_val": min_val,
        "max_val": max_val,
        "min_loc": min_loc,
        "max_loc": max_loc,
        "is_move_frame_result": is_move_frame_result,
        "gray_move_anker_template": frame_detector.gray_move_anker_template,
    }


def debug_move_extraction(frame, extractor):
    """Debug move extraction process step by step."""
    from config.config import (
        MOVE_SELECT_WINDOW1,
        MOVE_SELECT_WINDOW2,
        MOVE_SELECT_WINDOW3,
        MOVE_SELECT_WINDOW4,
        MOVE_TITLE1,
        MOVE_TITLE2,
        MOVE_TITLE3,
        MOVE_TITLE4,
    )

    # Extract move selection windows and calculate brightness
    move_select_windows = []
    move_title_windows = []
    move_windows_config = [
        (MOVE_SELECT_WINDOW1, MOVE_TITLE1, "Move 1"),
        (MOVE_SELECT_WINDOW2, MOVE_TITLE2, "Move 2"),
        (MOVE_SELECT_WINDOW3, MOVE_TITLE3, "Move 3"),
        (MOVE_SELECT_WINDOW4, MOVE_TITLE4, "Move 4"),
    ]

    move_info = []

    for i, (select_window_config, title_window_config, label) in enumerate(
        move_windows_config
    ):
        # Extract select window and calculate brightness
        select_window = frame[
            select_window_config[0] : select_window_config[1],
            select_window_config[2] : select_window_config[3],
        ]

        # Extract title window
        title_window = frame[
            title_window_config[0] : title_window_config[1],
            title_window_config[2] : title_window_config[3],
        ]

        brightness = np.mean(cv2.cvtColor(select_window, cv2.COLOR_BGR2GRAY))

        move_select_windows.append(select_window)
        move_title_windows.append(title_window)
        move_info.append(
            {
                "label": label,
                "brightness": brightness,
                "select_window": select_window,
                "title_window": title_window,
            }
        )

    # Find the brightest (selected) move
    max_brightness_index = np.argmax([info["brightness"] for info in move_info])

    # Try to extract move using the full extractor method
    try:
        move_result = extractor.extract_move(frame)
        extraction_success = True
        extraction_error = None
    except Exception as e:
        move_result = None
        extraction_success = False
        extraction_error = str(e)

    return {
        "move_info": move_info,
        "max_brightness_index": max_brightness_index,
        "move_result": move_result,
        "extraction_success": extraction_success,
        "extraction_error": extraction_error,
    }


def main():
    st.title("Pokemon Battle Frame Detector Debugger")

    # Sidebar for controls
    st.sidebar.header("Controls")

    # Language selection
    language = st.sidebar.selectbox("Select Language", ["en", "ja"], index=0)

    # Video file selection
    video_files = load_video_files()

    if not video_files:
        st.warning(
            "No video files found in 'video' directory. Please add some video files (.mp4, .avi, .mov, .mkv)."
        )
        st.info(
            "To add video files, place them in the 'video' directory in your project root."
        )
        return

    selected_video = st.sidebar.selectbox("Select Video File", video_files)

    if selected_video:
        video_path = Path("video") / selected_video

        # Initialize FrameDetector and Extractor
        frame_detector = FrameDetector(language)
        extractor = Extractor(language)

        # Frame number input
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        st.sidebar.write(f"Total Frames: {total_frames}")
        st.sidebar.write(f"FPS: {fps:.2f}")
        st.sidebar.write(f"Duration: {total_frames / fps:.2f}s")

        frame_number = st.sidebar.number_input(
            "Frame Number", min_value=0, max_value=total_frames - 1, value=0, step=1
        )

        # Frame range slider for quick navigation
        frame_range = st.sidebar.slider(
            "Frame Range Navigation",
            min_value=0,
            max_value=total_frames - 1,
            value=frame_number,
            step=1,
        )

        if frame_range != frame_number:
            frame_number = frame_range
            st.rerun()

        # Time-based navigation
        current_time = frame_number / fps
        st.sidebar.write(f"Current Time: {current_time:.2f}s")

        show_move_extract_debug_info = st.sidebar.checkbox(
            "Show Move Extract Debug Info", value=False
        )
        
        show_is_move_frame_debug = st.sidebar.checkbox(
            "Show is_move_frame Debug Info", value=False
        )

        # Load and display frame
        frame, _ = get_frame_from_video(video_path, frame_number)

        if frame is not None:
            # Convert BGR to RGB for proper display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Main content area
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader(f"Frame {frame_number}")

                # Display options
                show_regions = st.checkbox("Show Detection Regions", value=False)

                if show_regions:
                    frame_with_regions = draw_detection_regions(frame_rgb)
                    st.image(
                        frame_with_regions,
                        caption=f"Frame {frame_number} with detection regions",
                        width="stretch",
                    )
                else:
                    st.image(
                        frame_rgb,
                        caption=f"Frame {frame_number}",
                        width="stretch",
                    )

            with col2:
                st.subheader("Detection Results")

                # Test all frame detector methods
                results = test_frame_detector_methods(frame, frame_detector)

                # Display results in a nice format
                for method_name, result in results.items():
                    if isinstance(result, bool):
                        icon = "✅" if result else "❌"
                        st.markdown(f"**{method_name}**: {icon}")
                    else:
                        st.markdown(f"**{method_name}**: {result}")

                # Show summary
                true_count = sum(1 for r in results.values() if r is True)
                st.markdown(f"**Total Detections**: {true_count}/{len(results)}")

            if show_move_extract_debug_info:
                # Move extraction debugging (full width)
                st.subheader("Move Extraction Debug")

                # Check if this is a move frame
                is_move_frame = results.get("Move", False)

                if is_move_frame:
                    move_debug_info = debug_move_extraction(frame, extractor)

                    # Display move extraction results
                    if move_debug_info["extraction_success"]:
                        move_result = move_debug_info["move_result"]
                        st.success("✅ Move extraction successful!")
                        st.markdown(
                            f"**Selected Move**: {move_result.get('move', 'N/A')}"
                        )
                        st.markdown(
                            f"**Your Pokemon**: {move_result.get('your_pokemon_name', 'N/A')}"
                        )
                        st.markdown(
                            f"**Opponent Pokemon**: {move_result.get('opponent_pokemon_name', 'N/A')}"
                        )
                    else:
                        st.error(
                            f"❌ Move extraction failed: {move_debug_info['extraction_error']}"
                        )

                    # Display brightness values for each move window
                    st.markdown("**Move Window Brightness Values:**")
                    max_brightness_index = move_debug_info["max_brightness_index"]

                    for i, move_info in enumerate(move_debug_info["move_info"]):
                        brightness = move_info["brightness"]
                        is_selected = i == max_brightness_index
                        icon = "🔆" if is_selected else "🔅"
                        style = "**" if is_selected else ""
                        st.markdown(
                            f"{style}{icon} {move_info['label']}: {brightness:.2f}{style}"
                        )

                    # Show individual move windows
                    st.markdown("**Move Windows Preview:**")

                    # Display move selection windows (brightness indicators)
                    col1, col2, col3, col4 = st.columns(4)
                    cols = [col1, col2, col3, col4]

                    for i, move_info in enumerate(move_debug_info["move_info"]):
                        with cols[i]:
                            select_window = cv2.cvtColor(
                                move_info["select_window"], cv2.COLOR_BGR2RGB
                            )
                            title_window = cv2.cvtColor(
                                move_info["title_window"], cv2.COLOR_BGR2RGB
                            )

                            is_selected = i == max_brightness_index

                            st.markdown(
                                f"**{move_info['label']}** {'(SELECTED)' if is_selected else ''}"
                            )
                            st.image(
                                select_window,
                                caption=f"Brightness: {move_info['brightness']:.2f}",
                                width=120,
                            )
                            st.image(title_window, caption="Title Window", width=120)

                else:
                    st.info(
                        "ℹ️ This is not a move frame. Move debugging is only available for move frames."
                    )
                    
            # Detailed is_move_frame debug section
            if show_is_move_frame_debug:
                st.subheader("is_move_frame Debug Details")
                
                # Get detailed debug info
                move_frame_debug = debug_is_move_frame(frame, frame_detector)
                
                # Display configuration values
                st.markdown("**Configuration:**")
                st.markdown(f"- **MOVE_ANKER_POSITION**: {move_frame_debug['move_anker_position']}")
                st.markdown(f"- **MOVE_ANKER_THRESHOLD**: {move_frame_debug['move_anker_threshold']}")
                
                # Display template matching results
                st.markdown("**Template Matching Results:**")
                st.markdown(f"- **Min Value**: {move_frame_debug['min_val']:.6f}")
                st.markdown(f"- **Max Value**: {move_frame_debug['max_val']:.6f}")
                st.markdown(f"- **Min Location**: {move_frame_debug['min_loc']}")
                st.markdown(f"- **Max Location**: {move_frame_debug['max_loc']}")
                
                # Display the final result
                result_color = "success" if move_frame_debug['is_move_frame_result'] else "error"
                result_icon = "✅" if move_frame_debug['is_move_frame_result'] else "❌"
                
                if move_frame_debug['is_move_frame_result']:
                    st.success(f"{result_icon} **is_move_frame Result**: True (Max value {move_frame_debug['max_val']:.6f} >= Threshold {move_frame_debug['move_anker_threshold']})")
                else:
                    st.error(f"{result_icon} **is_move_frame Result**: False (Max value {move_frame_debug['max_val']:.6f} < Threshold {move_frame_debug['move_anker_threshold']})")
                
                # Display extracted area and template
                st.markdown("**Visual Comparison:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Extracted Move Anchor Area**")
                    st.image(
                        move_frame_debug['gray_move_anker_area'], 
                        caption=f"Shape: {move_frame_debug['gray_move_anker_area'].shape}",
                        width=200
                    )
                
                with col2:
                    st.markdown("**Template**")
                    st.image(
                        move_frame_debug['gray_move_anker_template'], 
                        caption=f"Shape: {move_frame_debug['gray_move_anker_template'].shape}",
                        width=200
                    )
                
                with col3:
                    st.markdown("**Match Result Heatmap**")
                    # Normalize the result for better visualization
                    normalized_result = cv2.normalize(move_frame_debug['template_match_result'], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                    # Apply colormap for better visualization
                    colored_result = cv2.applyColorMap(normalized_result, cv2.COLORMAP_JET)
                    st.image(
                        cv2.cvtColor(colored_result, cv2.COLOR_BGR2RGB),
                        caption=f"Shape: {move_frame_debug['template_match_result'].shape}",
                        width=200
                    )
                
                # Additional analysis
                st.markdown("**Analysis:**")
                threshold_diff = move_frame_debug['max_val'] - move_frame_debug['move_anker_threshold']
                if threshold_diff > 0:
                    st.markdown(f"- Match exceeds threshold by: **{threshold_diff:.6f}**")
                else:
                    st.markdown(f"- Match falls short of threshold by: **{abs(threshold_diff):.6f}**")
                
                confidence_pct = move_frame_debug['max_val'] * 100
                st.markdown(f"- Template matching confidence: **{confidence_pct:.2f}%**")

            # Navigation buttons
            st.subheader("Quick Navigation")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                if st.button("⏮️ First Frame"):
                    st.session_state.frame_number = 0
                    st.rerun()

            with col2:
                if st.button("⏪ -100 Frames"):
                    new_frame = max(0, frame_number - 100)
                    st.session_state.frame_number = new_frame
                    st.rerun()

            with col3:
                if st.button("⏪ -10 Frames"):
                    new_frame = max(0, frame_number - 10)
                    st.session_state.frame_number = new_frame
                    st.rerun()

            with col4:
                if st.button("⏩ +10 Frames"):
                    new_frame = min(total_frames - 1, frame_number + 10)
                    st.session_state.frame_number = new_frame
                    st.rerun()

            with col5:
                if st.button("⏩ +100 Frames"):
                    new_frame = min(total_frames - 1, frame_number + 100)
                    st.session_state.frame_number = new_frame
                    st.rerun()

            # Batch analysis
            st.subheader("Batch Analysis")

            if st.button("Analyze Detection Patterns (Sample 100 frames)"):
                with st.spinner("Analyzing frames..."):
                    sample_frames = np.linspace(0, total_frames - 1, 100, dtype=int)
                    batch_results = {}

                    for sample_frame in sample_frames:
                        test_frame, _ = get_frame_from_video(video_path, sample_frame)
                        if test_frame is not None:
                            frame_results = test_frame_detector_methods(
                                test_frame, frame_detector
                            )
                            for method, result in frame_results.items():
                                if method not in batch_results:
                                    batch_results[method] = []
                                batch_results[method].append((sample_frame, result))

                    # Display batch results
                    for method, results in batch_results.items():
                        positive_frames = [
                            frame_num for frame_num, result in results if result is True
                        ]
                        st.write(
                            f"**{method}**: {len(positive_frames)} positive detections"
                        )
                        if positive_frames:
                            st.write(
                                f"Frame numbers: {positive_frames[:10]}{'...' if len(positive_frames) > 10 else ''}"
                            )

        else:
            st.error(f"Could not load frame {frame_number}")


if __name__ == "__main__":
    main()
