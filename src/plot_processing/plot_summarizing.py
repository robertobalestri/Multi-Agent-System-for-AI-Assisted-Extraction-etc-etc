from typing import List, Dict
from textwrap import dedent
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from src.utils.logger_utils import setup_logging
from src.utils.text_utils import load_text
from src.utils.llm_utils import clean_llm_text_response
import os

logger = setup_logging(__name__)

def summarize_plot(text: str, llm: AzureChatOpenAI, output_path: str) -> str:
    """
    Summarize the plot of a series using the LLM.
    
    Args:
        text (str): The text to summarize
        llm (AzureChatOpenAI): The LLM to use
        output_path (str): Where to save the summary
        
    Returns:
        str: The summarized text
    """
    prompt = dedent(f"""You are an expert at summarizing the main narrative arcs and plot progression of TV series.
    You will receive a plot description for a TV series and need to summarize it, focusing on the key narrative arcs and progression, while preserving the storyline without extraneous details.
    Your summary should be linear, capturing the primary events and shifts in the plot in a detailed, chronological manner without skipping around the text or adding commentary.
    Avoid conclusions or personal interpretation.
    Please summarize the following text:\n{text}""")
    
    response = llm.invoke([HumanMessage(content=prompt)])
    summary = clean_llm_text_response(response.content.strip())
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as output_file:
        output_file.write(summary)
    
    return summary

def create_season_summary(episode_plots_paths: List[str], llm: AzureChatOpenAI, season_summary_path: str) -> str:
    """
    Create a season summary from individual episode summaries.
    
    Args:
        episode_plots_paths (List[str]): List of paths to episode plot files
        llm (AzureChatOpenAI): The LLM to use
        season_summary_path (str): Where to save the season summary
        
    Returns:
        str: The season summary
    """
    # First summarize each episode
    episode_summaries: Dict[str, str] = {}
    for plot_path in episode_plots_paths:
        if not os.path.exists(plot_path):
            logger.warning(f"Plot file not found: {plot_path}")
            continue
            
        plot_text = load_text(plot_path)
        summary_path = plot_path.replace("_plot.txt", "_summarized_plot.txt")
        
        # Check if summary already exists
        if os.path.exists(summary_path):
            logger.info(f"Loading existing summary from: {summary_path}")
            with open(summary_path, "r") as f:
                summary = f.read()
        else:
            logger.info(f"Creating new summary for: {plot_path}")
            summary = summarize_plot(plot_text, llm, summary_path)
            
        episode_summaries[plot_path] = summary
    
    if not episode_summaries:
        logger.warning("No episode summaries created or found")
        return ""
    
    # Then combine and summarize all episodes together enumerating the episode number
    combined_summaries = []
    episode_number = 1
    for episode_summary in episode_summaries.values():
        episode_summary = f"#{episode_number}. {episode_summary}"
        episode_number += 1
        combined_summaries.append(episode_summary)
    
    prompt = dedent(f"""You are an expert at creating cohesive season summaries for TV series by focusing on the primary narrative arcs and plot evolution. You also love spoilers, so you don't keep secrets on the plot, you're not writing for a Coming Soon journal.
    You will receive multiple episode summaries, separated by 'EPISODE BREAK,' and are to create a season summary that preserves the chronological development of the main storyline.
    Each episode's summary should remain in order without mixing events from different episodes. Mantain the order and divisions of the episodes.
    You will focus on the narrative arcs that spans multiple episodes, not the episodic arcs that only happen in a single episode.
    Emphasize key developments and character arcs without adding extraneous details, conclusions, or commentary.
    Please create a season summary from these episode summaries:\n{combined_summaries}""")
    
    response = llm.invoke([HumanMessage(content=prompt)])
    season_summary = clean_llm_text_response(response.content.strip())
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(season_summary_path), exist_ok=True)
    
    with open(season_summary_path, "w") as season_file:
        season_file.write(season_summary)
        
    return season_summary
