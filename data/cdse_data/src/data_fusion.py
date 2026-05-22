from pathlib import Path
import pandas as pd


def _combine_chunks(file_list):
    dataframes = []
    for file_path in file_list:
        if file_path.exists():
            df = pd.read_csv(file_path)
            dataframes.append(df)
        else:
            print(f"{file_path.name} does not exist")

    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    return None

def merge_pipelines(ndvi_files, weather_files, final_output_path):

    print("combine NDVI chunks")
    df_ndvi = _combine_chunks(ndvi_files)

    print("combine WEATHER chunks")
    df_weather = _combine_chunks(weather_files)

    if df_ndvi is not None and df_weather is not None:
        print("fuse NDVI and WEATHER")

        df_final = pd.merge(
            df_ndvi,
            df_weather,
            on=['date', 'feature_index'],
            how='inner' # Behält nur Zeilen, an denen wir für den Tag SOWOHL NDVI als auch Wetter haben
        )

        final_output_path.parent.mkdir(parents=True, exist_ok=True)
        df_final.to_csv(final_output_path, index=False)

    else:
        print("ERROR, Data missing")
