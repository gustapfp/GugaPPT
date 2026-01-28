import uuid


def generate_pprt_id(topic: str) -> str:
    """Generate a unique presentation ID based on the topic.

    Args:
        topic (str): The topic of the presentation.

    Returns:
        str: The unique presentation ID.
    """
    return f"{topic}-{uuid.uuid4()}"
