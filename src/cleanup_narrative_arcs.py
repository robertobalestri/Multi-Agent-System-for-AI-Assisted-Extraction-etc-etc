import os
import shutil
from typing import List
from path_handler import PathHandler

def get_episodes_in_season(season_path: str) -> List[str]:
    """Get list of episode folders in a season directory."""
    return [ep for ep in os.listdir(season_path) if os.path.isdir(os.path.join(season_path, ep))]

def delete_narrative_arcs_and_entities(series: str, season: str):
    """Delete only narrative arcs related files and databases."""
    base_dir = "data"  # Base directory for data
    chroma_db_path = os.path.join('chroma_db')  # Path to the @chroma_db folder
    database_path = os.path.join('narrative.db')


    should_delete_analysis = True
    should_delete_entities = True

    # Delete the database file if it exists
    if os.path.exists(database_path):
        os.remove(database_path)
        print(f"Deleted file: {database_path}")
    else:
        print(f"File not found: {database_path}")

    # Delete the @chroma_db folder if it exists
    if os.path.exists(chroma_db_path):
        shutil.rmtree(chroma_db_path)
        print(f"Deleted folder: {chroma_db_path}")
    else:
        print(f"Folder not found: {chroma_db_path}")

    # Construct the path for the season directory
    season_path = os.path.join(base_dir, series, season)

    # Check if the season directory exists
    if os.path.exists(season_path):
        print(f"Season directory found: {season_path}")

        extracted_entities_path = os.path.join(base_dir, series, season, f"{series}{season}_extracted_entities.json")
        if os.path.exists(extracted_entities_path):
            os.remove(extracted_entities_path)
            print(f"Deleted file: {extracted_entities_path}")

        # Delete the multiagent episode narrative arcs JSON files
        for episode in os.listdir(season_path):
            episode_path = os.path.join(season_path, episode)
            if os.path.isdir(episode_path):
                episode_narrative_arcs_path = os.path.join(episode_path, f"{series}{season}{episode}_multiagent_suggested_episode_arcs.json")
                if os.path.exists(episode_narrative_arcs_path):
                    os.remove(episode_narrative_arcs_path)
                    print(f"Deleted file: {episode_narrative_arcs_path}")
                
                if should_delete_entities:
                    plot_entities_normalized_path = os.path.join(episode_path, f"{series}{season}{episode}_plot_entities_normalized.txt")
                    plot_entities_substituted_path = os.path.join(episode_path, f"{series}{season}{episode}_plot_entities_substituted.txt")
                    raw_spacy_entities_path = os.path.join(episode_path, f"{series}{season}{episode}_raw_spacy_entities.json")
                    refined_entities_path = os.path.join(episode_path, f"{series}{season}{episode}_refined_entities.json")
                    if os.path.exists(plot_entities_normalized_path):
                        os.remove(plot_entities_normalized_path)
                    print(f"Deleted file: {plot_entities_normalized_path}")
                    if os.path.exists(plot_entities_substituted_path):
                        os.remove(plot_entities_substituted_path)
                        print(f"Deleted file: {plot_entities_substituted_path}")
                    if os.path.exists(raw_spacy_entities_path):
                        os.remove(raw_spacy_entities_path)
                        print(f"Deleted file: {raw_spacy_entities_path}")
                    if os.path.exists(refined_entities_path):
                        os.remove(refined_entities_path)
                        print(f"Deleted file: {refined_entities_path}")
                
                else:
                    print(f"File not found: {episode_narrative_arcs_path}")

        # ANALYSIS FILES
        
        # Delete the multiagent season narrative analysis file
        if should_delete_analysis:
            season_narrative_analysis_path = os.path.join(season_path, f"{series}{season}_multiagent_season_narrative_analysis.txt")
            if os.path.exists(season_narrative_analysis_path):
                os.remove(season_narrative_analysis_path)
                print(f"Deleted file: {season_narrative_analysis_path}")
            else:
                print(f"File not found: {season_narrative_analysis_path}")

        # Delete the multiagent episode narrative analysis files
        for episode in os.listdir(season_path):
            episode_path = os.path.join(season_path, episode)
            if os.path.isdir(episode_path):
                episode_narrative_analysis_path = os.path.join(episode_path, f"{series}{season}{episode}_multiagent_episode_narrative_analysis.txt")
                if should_delete_analysis:
                    if os.path.exists(episode_narrative_analysis_path):
                        os.remove(episode_narrative_analysis_path)
                        print(f"Deleted file: {episode_narrative_analysis_path}")
                else:
                    print(f"File not found: {episode_narrative_analysis_path}")
        
    else:
        print(f"Season directory not found: {season_path}")

def deep_clean_season(series: str, season: str):
    """Perform deep cleaning of generated files while preserving original data."""
    base_dir = "data"  # Base directory for data
    chroma_db_path = os.path.join('chroma_db')  # Path to the @chroma_db folder
    database_path = os.path.join('narrative.db')

    # Delete the database file if it exists
    if os.path.exists(database_path):
        os.remove(database_path)
        print(f"Deleted file: {database_path}")
    else:
        print(f"File not found: {database_path}")

    # Delete the @chroma_db folder if it exists
    if os.path.exists(chroma_db_path):
        shutil.rmtree(chroma_db_path)
        print(f"Deleted folder: {chroma_db_path}")
    else:
        print(f"Folder not found: {chroma_db_path}")

    # Construct the path for the season directory
    season_path = os.path.join(base_dir, series, season)

    # Check if the season directory exists
    if os.path.exists(season_path):
        print(f"Season directory found: {season_path}")
        
        # Delete season-level files
        for episode in get_episodes_in_season(season_path):
            episode_path = os.path.join(season_path, episode)
            path_handler = PathHandler(series, season, episode)
            
            # List of files to preserve (add more if needed)
            preserve_patterns = [
                "_plot.txt",
                "_full_dialogues.json"
            ]
            
            # Delete all files in episode directory except those matching preserve patterns
            if os.path.isdir(episode_path):
                for file in os.listdir(episode_path):
                    file_path = os.path.join(episode_path, file)
                    if os.path.isfile(file_path):
                        # Check if file should be preserved
                        should_preserve = any(pattern in file for pattern in preserve_patterns)
                        if not should_preserve:
                            os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                        else:
                            print(f"Preserved file: {file_path}")

        # Delete season-level generated files
        season_files_to_delete = [
            path_handler.get_season_narrative_arcs_path(),
            path_handler.get_season_narrative_analysis_path(),
            path_handler.get_season_extracted_refined_entities_path(),
        ]

        for file_path in season_files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted season-level file: {file_path}")
            
    else:
        print(f"Season directory not found: {season_path}")

if __name__ == "__main__":
    # Replace these with the actual series and season names you want to clean up
    series_name = "GA"  # e.g., "MyShow"
    season_name = "S01"  # e.g., "Season1"
    
    # Choose which cleanup function to run
    delete_narrative_arcs_and_entities(series_name, season_name)  # For narrative arcs only
    #deep_clean_season(series_name, season_name)    # For full cleanup
