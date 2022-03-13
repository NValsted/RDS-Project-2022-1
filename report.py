from io import StringIO

from src.stats import generate_figures, profile_report
from src.mail import send_email


def send_report():
    pandas_profile = profile_report()
    distplot, scatter = generate_figures()

    logs = StringIO()
    with open("logs.log", "r") as f:
        logs.write(f.read())

    pandas_profile_stream = StringIO()
    pandas_profile_stream.write(pandas_profile.to_html())

    scatter_stream = StringIO()
    scatter_stream.write(scatter.to_html())

    distplot_stream = StringIO()
    distplot_stream.write(distplot.to_html())

    send_email(
        attachments=[
            ("pandas-profiling-report.html", pandas_profile_stream),
            ("scatter.html", scatter_stream),
            ("distplot.html", distplot_stream),
            ("logs.log", logs),
        ],
    )


if __name__ == "__main__":
    send_report()
