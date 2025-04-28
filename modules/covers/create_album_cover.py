"""
module/albumCovers/create_album_cover.py

Orchestrates creation of album cover images using configurations loaded
from config/settings.py. All scaling/positioning is user-adjustable via
albumCoverConfig.json.
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from config.settings import (
    CONFIGURATIONS,
    PASTE_LOGO,
    ORIGINAL_IMAGES_FOLDER,
    DESTINATION_FOLDER,
    OUTPUT_FOLDER
)

# Color Codes & Message Prefixes
COLOR_RESET  = "\033[0m"
COLOR_RED    = "\033[31m"
COLOR_GREEN  = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE   = "\033[34m"
COLOR_CYAN   = "\033[36m"
COLOR_GREY   = "\033[37m"

MSG_ERROR   = f"{COLOR_RED}[Error]{COLOR_RESET}: "
MSG_NOTICE  = f"{COLOR_YELLOW}[Notice]{COLOR_RESET}: "
MSG_DEBUG   = f"{COLOR_CYAN}[Debug]{COLOR_RESET}: "
MSG_SUCCESS = f"{COLOR_GREEN}[Success]{COLOR_RESET}: "
MSG_STATUS  = f"{COLOR_GREEN}[Status]{COLOR_RESET}: "
MSG_WARNING = f"{COLOR_BLUE}[Warning]{COLOR_RESET}: "
LINE_BREAK  = f"{COLOR_GREY}----------------------------------------{COLOR_RESET}"

def determine_font_scaling_main(config, mix_number):
    """
    Returns the adjusted `font_scaling_main` based on mix_number thresholds.
    If no override applies, uses the config's default `font_scaling_main`.
    """
    base_scaling = config.get("font_scaling_main", 0.2)
    overrides = config.get("mix_number_overrides", [])

    # Sort overrides by ascending threshold
    # so we can apply the largest threshold that is <= mix_number
    # if mix_number > threshold
    overrides_sorted = sorted(overrides, key=lambda o: o["threshold"])

    for override in overrides_sorted:
        # e.g. if threshold=99 and mix_number=100 => we apply the override
        if mix_number > override["threshold"]:
            base_scaling = override["font_scaling_main"]
        else:
            break

    return base_scaling

def create_album_cover(config, image_path, mix_number, output_path):
    """
    Creates an album cover image using dynamic scaling & positions from config.
    Returns True on success, False on error.
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            new_size = min(width, height)

            left = (width - new_size) / 2
            top  = (height - new_size) / 2

            img_cropped = img.crop((left, top, left + new_size, top + new_size))
            cropped_width, cropped_height = img_cropped.size

            # Semi-transparent overlay
            overlay = Image.new('RGBA', img_cropped.size, (0, 0, 0, int(255 * 0.25)))
            img_with_overlay = Image.alpha_composite(img_cropped.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img_with_overlay)

            # 1) Font Size Calculation
            # subheading
            subheading_scale = config.get("font_scaling_subheading", 0.06)
            multiplier = config.get("font_scaling_multiplier", 2.3)
            font_size_subheading = int(cropped_width * subheading_scale * multiplier)

            # main text
            main_scale = determine_font_scaling_main(config, mix_number)
            font_size_main = int(cropped_width * main_scale * multiplier)

            font_subheading = ImageFont.truetype(config["font_path"], size=font_size_subheading)
            font_main       = ImageFont.truetype(config["font_path"], size=font_size_main)

            # 2) If user wants to paste a logo, load & resize it
            logo_img = None
            if PASTE_LOGO and os.path.exists(config["logo_path"]):
                logo_factor = config.get("positions", {}).get("logo_size_factor", 0.1)
                logo_size = (
                    int(cropped_width * logo_factor),
                    int(cropped_width * logo_factor)
                )
                with Image.open(config["logo_path"]) as temp_logo:
                    logo_img = temp_logo.resize(logo_size, Image.Resampling.LANCZOS)

            # 3) Prepare texts
            subheading_text_1 = config["subheading_text_1"].format(mix_number=mix_number)
            subheading_text_2 = config["subheading_text_2"]
            main_text         = config["main_text_template"].format(mix_number=mix_number)

            # 4) Vertical Layout
            vertical_gap   = int(cropped_height * 0.05)
            subheading_1_y = vertical_gap
            subheading_2_y = cropped_height - font_size_subheading - vertical_gap

            # 5) Position logic based on 'active_flag'
            # If you have more advanced layout needs, you can move them into 'positions' inside JSON
            active_flag = config["active_flag"]

            if active_flag == "CUE_CLUB_ARCHIVE":
                # Example: subheading positions
                draw.text((cropped_width // 12, subheading_1_y),
                          subheading_text_1, font=font_subheading, fill="white")
                draw.text((cropped_width // 7, subheading_2_y),
                          subheading_text_2, font=font_subheading, fill="white")

                # main text position depends on mix_number
                if mix_number == 1:
                    main_text_x = cropped_width // 2.22
                elif 1 < mix_number < 10:
                    main_text_x = cropped_width // 3
                elif 9 < mix_number < 100:
                    main_text_x = cropped_width // 7
                else:
                    main_text_x = cropped_width // 5

                main_text_y = int((cropped_height - font_size_main) / 2)
                draw.text((main_text_x, main_text_y), main_text, font=font_main, fill="white")

                # paste logo if loaded
                if logo_img:
                    logo_x = (cropped_width - logo_img.width) // 2
                    # For large mix_number offset:
                    if mix_number >= 100:
                        logo_y = main_text_y + font_size_main + 125
                    else:
                        logo_y = main_text_y + font_size_main
                    img_with_overlay.paste(logo_img, (int(logo_x), int(logo_y)), logo_img)

            elif active_flag == "LATE_NIGHT_BREAKFAST":
                draw.text((cropped_width // 23, subheading_1_y),
                          subheading_text_1, font=font_subheading, fill="white")
                draw.text((cropped_width // 12, subheading_2_y),
                          subheading_text_2, font=font_subheading, fill="white")

                main_text_x = cropped_width // 19
                main_text_y = int((cropped_height - font_size_main) / 2)
                draw.text((main_text_x, main_text_y), main_text, font=font_main, fill="white")

                if logo_img:
                    logo_x = (cropped_width - logo_img.width) // 2
                    logo_y = main_text_y + font_size_main
                    img_with_overlay.paste(logo_img, (int(logo_x), int(logo_y)), logo_img)

            elif active_flag == "KICKSWAP":
                draw.text((cropped_width // 12, subheading_1_y),
                          subheading_text_1, font=font_subheading, fill="white")
                draw.text((cropped_width // 7, subheading_2_y),
                          subheading_text_2, font=font_subheading, fill="white")

                if mix_number == 1:
                    main_text_x = cropped_width // 2.22
                elif 1 < mix_number < 10:
                    main_text_x = cropped_width // 3
                elif 9 < mix_number < 100:
                    main_text_x = cropped_width // 7
                else:
                    main_text_x = cropped_width // 10

                main_text_y = int((cropped_height - font_size_main) / 2)
                draw.text((main_text_x, main_text_y), main_text, font=font_main, fill="white")

                if logo_img:
                    logo_x = (cropped_width - logo_img.width) // 2
                    logo_y = main_text_y + font_size_main
                    img_with_overlay.paste(logo_img, (int(logo_x), int(logo_y)), logo_img)

            else:
                # Default fallback
                draw.text((cropped_width // 12, subheading_1_y),
                          subheading_text_1, font=font_subheading, fill="white")
                draw.text((cropped_width // 7, subheading_2_y),
                          subheading_text_2, font=font_subheading, fill="white")
                main_text_x = cropped_width // 7
                main_text_y = int((cropped_height - font_size_main) / 2)
                draw.text((main_text_x, main_text_y), main_text, font=font_main, fill="white")

                if logo_img:
                    logo_x = (cropped_width - logo_img.width) // 2
                    logo_y = main_text_y + font_size_main
                    img_with_overlay.paste(logo_img, (int(logo_x), int(logo_y)), logo_img)

            # Save final
            img_with_overlay.save(output_path)
            return True

    except IOError:
        print(f"{MSG_ERROR}Cannot process image file: {image_path}")
        return False
    except Exception as e:
        print(f"{MSG_ERROR}Unexpected error: {e}")
        return False

def move_original_image(image_path, destination_folder):
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.move(image_path, os.path.join(destination_folder, os.path.basename(image_path)))
    except Exception as e:
        print(f"{MSG_ERROR}Could not move file {image_path} => {destination_folder}: {e}")

def get_configuration():
    """
    Let the user select from the keys in CONFIGURATIONS (in albumCoverConfig.json).
    If no configurations exist, prompt the user to create a default file.
    """
    # Check if configurations dictionary is empty
    if not CONFIGURATIONS:
        print(f"{MSG_WARNING}No configurations found!")
        print(f"{MSG_NOTICE}Please create a default configuration file in the configuration folder first.")
        return None
    
    print(f"{MSG_STATUS}Available Configurations:")
    config_names = list(CONFIGURATIONS.keys())
    for idx, name in enumerate(config_names, start=1):
        print(f"{idx}. {name}")

    while True:
        try:
            choice = int(input(f"{MSG_NOTICE}Select a configuration by number: "))
            if 1 <= choice <= len(config_names):
                chosen_name = config_names[choice - 1]
                return CONFIGURATIONS[chosen_name]
            else:
                print(f"{MSG_WARNING}Invalid selection. Please try again.")
        except ValueError:
            print(f"{MSG_WARNING}Please enter a valid number.")

def test_run_album_covers():
    """
    Perform a test run of album cover generation.
    Displays previews of album covers without saving or moving files.
    Users can iterate through images or quit the test at any time.
    """
    # 1) Ask user which configuration to use
    config = get_configuration()

    # 2) Validate paths
    if not os.path.exists(config["font_path"]):
        print(f"{MSG_ERROR}Font file not found: {config['font_path']}")
        return
    if PASTE_LOGO and not os.path.exists(config["logo_path"]):
        print(f"{MSG_ERROR}Logo file not found: {config['logo_path']}")
        return

    # 3) Check if the original images folder exists
    if not os.path.exists(ORIGINAL_IMAGES_FOLDER):
        print(f"{MSG_ERROR}Folder not found: {ORIGINAL_IMAGES_FOLDER}")
        return

    # 4) Gather images
    image_files = sorted(
        f for f in os.listdir(ORIGINAL_IMAGES_FOLDER)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    )
    if not image_files:
        print(f"{MSG_ERROR}No images found in {ORIGINAL_IMAGES_FOLDER}")
        print(f"{MSG_NOTICE}Please use 'djcli dl_pexel' to download images.")
        return

    # 5) Ask for starting mix number
    while True:
        try:
            starting_mix_number = int(input(f"{MSG_NOTICE}Enter the starting mix number for the test run: "))
            if starting_mix_number < 1:
                print(f"{MSG_WARNING}Mix number must be >= 1.")
                continue
            break
        except ValueError:
            print(f"{MSG_WARNING}Invalid number. Try again.")

    # 6) Process each image for preview
    mix_number = starting_mix_number
    for image_name in image_files:
        if image_name.startswith('.'):
            # skip hidden files (like .DS_Store on macOS)
            continue

        image_path = os.path.join(ORIGINAL_IMAGES_FOLDER, image_name)
        print(f"{MSG_STATUS}Previewing '{image_name}' with Mix Number: {mix_number}")

        # Generate a preview
        try:
            with Image.open(image_path) as img:
                # Create the album cover image in memory
                with Image.open(image_path) as img:
                    width, height = img.size
                    new_size = min(width, height)

                    left = (width - new_size) / 2
                    top = (height - new_size) / 2
                    img_cropped = img.crop((left, top, left + new_size, top + new_size))
                    cropped_width, cropped_height = img_cropped.size

                    # Semi-transparent overlay
                    overlay = Image.new('RGBA', img_cropped.size, (0, 0, 0, int(255 * 0.25)))
                    img_with_overlay = Image.alpha_composite(img_cropped.convert('RGBA'), overlay).convert('RGB')
                    draw = ImageDraw.Draw(img_with_overlay)

                    # Font Size Calculation
                    subheading_scale = config.get("font_scaling_subheading", 0.06)
                    multiplier = config.get("font_scaling_multiplier", 2.3)
                    font_size_subheading = int(cropped_width * subheading_scale * multiplier)

                    main_scale = determine_font_scaling_main(config, mix_number)
                    font_size_main = int(cropped_width * main_scale * multiplier)

                    font_subheading = ImageFont.truetype(config["font_path"], size=font_size_subheading)
                    font_main = ImageFont.truetype(config["font_path"], size=font_size_main)

                    # Prepare texts
                    subheading_text_1 = config["subheading_text_1"].format(mix_number=mix_number)
                    subheading_text_2 = config["subheading_text_2"]
                    main_text = config["main_text_template"].format(mix_number=mix_number)

                    # Vertical Layout
                    vertical_gap = int(cropped_height * 0.05)
                    subheading_1_y = vertical_gap
                    subheading_2_y = cropped_height - font_size_subheading - vertical_gap

                    draw.text((cropped_width // 12, subheading_1_y),
                              subheading_text_1, font=font_subheading, fill="white")
                    draw.text((cropped_width // 7, subheading_2_y),
                              subheading_text_2, font=font_subheading, fill="white")

                    main_text_x = cropped_width // 7
                    main_text_y = int((cropped_height - font_size_main) / 2)
                    draw.text((main_text_x, main_text_y), main_text, font=font_main, fill="white")

                    # Display the preview
                    img_with_overlay.show()

        except Exception as e:
            print(f"{MSG_ERROR}Error processing '{image_name}': {e}")
            continue

        # Ask user if they want to continue
        user_input = input(f"{MSG_NOTICE}Continue to the next image? (y/n): ").strip().lower()
        if user_input != 'y':
            print(f"{MSG_STATUS}Test run terminated by user.")
            break

        mix_number += 1

    print(f"{MSG_STATUS}Test run completed.")

def main():
    # 1) Ask user which configuration to use
    config = get_configuration()

    # 2) Validate paths
    if not os.path.exists(config["font_path"]):
        print(f"{MSG_ERROR}Font file not found: {config['font_path']}")
        return
    if PASTE_LOGO and not os.path.exists(config["logo_path"]):
        print(f"{MSG_ERROR}Logo file not found: {config['logo_path']}")
        return

    # 3) Check if the original images folder exists
    if not os.path.exists(ORIGINAL_IMAGES_FOLDER):
        print(f"{MSG_ERROR}Folder not found: {ORIGINAL_IMAGES_FOLDER}")
        return

    # 4) Create output folder if needed
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 5) Ask for starting mix number
    while True:
        try:
            starting_mix_number = int(input(f"{MSG_NOTICE}Enter the starting mix number: "))
            if starting_mix_number < 1:
                print(f"{MSG_WARNING}Mix number must be >= 1.")
                continue
            if starting_mix_number > 99999:
                print(f"{MSG_WARNING}Max allowed mix_number is 99999. Try again.")
                continue
            break
        except ValueError:
            print(f"{MSG_WARNING}Invalid number. Try again.")

    # 6) Gather images
    mix_number = starting_mix_number
    image_files = sorted(
        f for f in os.listdir(ORIGINAL_IMAGES_FOLDER)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    )
    if not image_files:
        print(f"{MSG_ERROR}No images found in {ORIGINAL_IMAGES_FOLDER}")
        print(f"{MSG_NOTICE}Please use 'djcli dl_pexel' to download images.")
        return

    # 7) Process each image
    for image_name in image_files:
        if image_name.startswith('.'):
            # skip hidden files (like .DS_Store on macOS)
            continue

        image_path = os.path.join(ORIGINAL_IMAGES_FOLDER, image_name)
        output_name = config["output_filename_template"].format(mix_number=mix_number)
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        print(f"{MSG_STATUS}Processing '{image_name}' => '{output_name}'")

        # create & save
        success = create_album_cover(config, image_path, mix_number, output_path)
        if success:
            # move original only if success & not debugging
            # if you want a debug toggle from JSON, add a "DEBUG" to GLOBAL_SETTINGS
            move_original_image(image_path, DESTINATION_FOLDER)
            print(f"{MSG_SUCCESS}Finished {image_name} => {output_name}")
        else:
            print(f"{MSG_WARNING}Skipping {image_name}")

        mix_number += 1
        if mix_number > 99999:
            print(f"{MSG_WARNING}Reached max allowed mix_number (99999). Stopping.")
            break

    print(f"{MSG_STATUS}All images processed.")