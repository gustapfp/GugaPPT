import json
from datetime import datetime
from typing import Literal

import numpy as np
from matplotlib import pyplot as plt
from mcp.server.fastmcp import FastMCP
from pptx import Presentation
from tavily import TavilyClient  # type: ignore

from core.consts import DOMAIN_BLACKLIST, FILE_PATH
from core.logger_config import logger
from core.settings import settings

mcp_server = FastMCP("PPT-Generator-Tools")

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)


@mcp_server.tool(
    name="search_web",
    description="Search the web for information",
)
def search_web(query: str, search_depth: Literal["basic", "advanced"] = "basic") -> str:
    """Search the web for information based on the given query.

    Args:
        query (str): The query to search the web for.
        search_depth (Literal["basic", "advanced"]): The depth of the search.
    Returns:
        str: The information searched for.
    """
    logger.info(
        f"Search Web Tool was triggered with query: {query}. Searching the web for information..."
    )
    try:
        response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=3,
            exclude_domains=DOMAIN_BLACKLIST,
        )

        context = [{"content": r["content"], "url": r["url"]} for r in response.get("results", [])]
        return json.dumps(context)
    except Exception as e:
        return f"Error searching web: {str(e)}"


@mcp_server.tool(
    name="create_presentation",
    description="Create a PowerPoint presentation based on the given slides content.",
)
def create_presentation(filename: str, slides_content: str) -> str:
    """Create a PowerPoint presentation based on the given slides content.

    Args:
        filename (str): The filename of the presentation.
        slides_content (str): The slides content of the presentation.

    Returns:
        str: The message indicating the success or failure of the operation.
    """
    try:
        data = json.loads(slides_content)
        prs = Presentation()

        for slide_data in data:
            # -- Bullet layout --
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)

            # -- Title --
            title = slide.shapes.title
            if title:
                title.text = slide_data.get("title", "No Title")

            # -- Body --
            body_shape = slide.placeholders[1]
            tf = body_shape.text_frame
            for point in slide_data.get("points", []):
                p = tf.add_paragraph()
                p.text = point

        path = FILE_PATH / f"{filename}.pptx"
        path.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(path.resolve()))
        return f"Successfully saved presentation to {path}"
    except Exception as e:
        return f"Error creating PPT: {str(e)}"


@mcp_server.tool(
    name="generate_visual_assets",
    description="Generate visual assets for the presentation.",
)
def generate_chart(data_json: str, chart_type: str, title: str) -> str:
    """
    Generates a statistical chart (bar, pie, or line) and saves it as a PNG image.

    Args:
        data_json: A JSON string containing 'labels' (list) and 'values' (list).
                   Example: '{"labels": ["Q1", "Q2"], "values": [100, 150]}'
        chart_type: The type of chart to generate. Options: "bar", "pie", "line".
        title: The title of the chart.

    Returns:
        The file path of the generated image.
    """
    logger.info(
        f"Generate Visual Assets Tool was triggered with data_json: {data_json}, chart_type: {chart_type}, title: {title}"
    )
    try:
        data = json.loads(data_json)
        labels = data.get("labels", [])
        values = data.get("values", [])

        if not labels or not values:
            raise ValueError("Error: JSON must contain 'labels' and 'values' lists.")

        if len(labels) != len(values):
            raise ValueError("Error: 'labels' and 'values' must have the same length.")

        plt.figure(figsize=(10, 6))

        if chart_type.lower() == "bar":
            plt.bar(labels, values, color="#4F81BD")
            plt.xlabel("Categories")
            plt.ylabel("Values")

        elif chart_type.lower() == "line":
            plt.plot(labels, values, marker="o", linestyle="-", color="#C0504D", linewidth=2)
            plt.grid(True, linestyle="--", alpha=0.7)

        elif chart_type.lower() == "pie":
            cmap = plt.get_cmap("Paired")
            rgba = cmap(np.linspace(0, 1, len(values)))
            colors = [tuple(rgba[i]) for i in range(len(values))]
            plt.pie(
                values,
                labels=labels,
                autopct="%1.0f%%",
                startangle=90,
                colors=colors,
            )
        else:
            return f"Error: Unsupported chart type '{chart_type}'. Use 'bar', 'pie', or 'line'."

        plt.title(title)

        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        timestamp = int(datetime.now().timestamp())
        filename = f"chart_{safe_title}_{timestamp}.png"
        path = FILE_PATH / "charts" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, bbox_inches="tight", dpi=100)
        plt.close()

        print(f"DEBUG: Saved chart to {path}")
        return str(path)

    except json.JSONDecodeError:
        return "Error: Invalid JSON string provided."
    except Exception as e:
        return f"Error generating chart: {str(e)}"


if __name__ == "__main__":
    mcp_server.run()
