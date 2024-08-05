from functions import export_raster_main, open_gee_project
import datetime
import pandas as pd
import sys
import multiprocessing
import ee
import tqdm

# Make tuples of function params


def gen_all_lakes_all_dates_params(
    out_dir,
    project,
    start_date_range,
    end_date_range,
    df_path,
    lagosid_path,
    frequency: int,
):
    print(df_path, lagosid_path)
    # read csvs
    df = pd.read_csv(df_path)

    lagosid = pd.read_csv(lagosid_path)
    print("CSV imported")

    # select relevant columns from lagosid
    lagosid = lagosid[["lagoslakei"]]
    df = pd.concat([lagosid, df], axis=1)
    # by merging, we only have lakes with insitu data
    # To get ALL ids, just use lagosid csv

    df = df[df["chl_a"] < 2000]

    df = df.drop_duplicates(subset=["lagoslakei"])

    df = df[["lagoslakei", "site"]]

    all_runs_needed = []
    for index, row in df.iterrows():
        lakeid = int(row["lagoslakei"])
        name = row["site"]
        formatted_name = name.lower().replace(" ", "-")

        date_range = list(
            pd.date_range(
                start=start_date_range, end=end_date_range, freq=f"{frequency}D"
            )
        )

        for i in range(len(date_range) - 1):  # stop iterating one element short
            start_date = date_range[i].strftime(
                f"%Y-%m-%d"
            )  # Small interval within the big interval
            end_date = date_range[i + 1].strftime(f"%Y-%m-%d")
            filename = formatted_name + "-" + start_date + "to" + end_date + ".tif"
            export_raster_main_nice_scale_params = [
                out_dir,
                filename,
                project,
                lakeid,
                start_date,
                end_date,
            ]
            all_runs_needed.append(export_raster_main_nice_scale_params)

    return all_runs_needed


def run_all_lakes_all_dates(
    out_dir,
    project,
    start_date_range,
    end_date_range,
    df_path,
    lagosid_path,
    frequency: int,
):
    manager = multiprocessing.Manager()
    scale_cache = manager.dict()  # empty by default
    pool = multiprocessing.Pool(25)

    all_params_to_pass_in = gen_all_lakes_all_dates_params(
        out_dir,
        project,
        start_date_range,
        end_date_range,
        tidy_df_path,
        lagosid_path,
        frequency,
    )

    for arr in all_params_to_pass_in:
        arr.append(
            scale_cache
        )  # pass in the scale cache at the end of the generated params
        # Works bc all_params is a list of references to arrs, which we are modifying

    # Starmap
    pool.imap(
        wrapper_export,
        tqdm.tqdm(all_params_to_pass_in, total=len(all_params_to_pass_in)),
    )
    pool.close()
    pool.join()


def wrapper_export(args):
    export_raster_main_nice_scale(*args)


def export_raster_main_nice_scale(
    out_dir, filename, project, lakeid: int, start_date, end_date, scale_cache
):

    scale = 20
    # while not successful
    while scale <= 40:
        try:
            # If scale has not been determined before
            if lakeid in scale_cache:
                # print("Using cached scale: ", scale_cache[lakeid])
                export_raster_main(
                    out_dir,
                    filename,
                    project,
                    lakeid,
                    start_date,
                    end_date,
                    scale_cache[lakeid],
                )
                break

            export_raster_main(
                out_dir,
                filename,
                project,
                lakeid,
                start_date,
                end_date,
                scale,
            )
            scale_cache[lakeid] = scale
            break  # If doesn't error, then just break
        except ee.ee_exception.EEException as error:
            if str(error).endswith("must be less than or equal to 50331648 bytes."):
                scale += 10  # Raise the scale by 10 and try again
            elif str(error).endswith(
                "Parameter 'object' is required."
            ):  # no images found
                # print("No images found")  # ignore
                break
            else:
                raise error
        except Exception as error:
            if str(error).endswith("not recognized as a supported file format."):
                # this happens if you write zero bytes to a tif with rasterio
                # TypeError: 'out_all/black-lake.tif' not recognized as a supported file format.

                scale += 10
            else:
                raise error


if __name__ == "__main__":
    project = sys.argv[1]
    out_dir = sys.argv[2]
    start_date_range = sys.argv[3]  # STR, in format YYYY-MM-DD
    end_date_range = sys.argv[4]  # STR, in format YYYY-MM-DD
    tidy_df_path = sys.argv[5]
    lagosid_path = sys.argv[6]
    frequency = int(sys.argv[7])

    open_gee_project(project=project)

    run_all_lakes_all_dates(
        out_dir,
        project,
        start_date_range,
        end_date_range,
        tidy_df_path,
        lagosid_path,
        frequency,
    )
