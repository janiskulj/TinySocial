from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
from tinydb import TinyDB


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_PATH=Path(app.instance_path) / "tinysocial.json",
    )

    if test_config:
        app.config.update(test_config)

    database_path = Path(app.config["DATABASE_PATH"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    def load_posts():
        with TinyDB(database_path) as db:
            return sorted(db.all(), key=lambda post: post["created_at"], reverse=True)

    @app.get("/")
    def index():
        return render_template("index.html", posts=load_posts())

    @app.post("/posts")
    def create_post():
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        if author and content:
            created_at = datetime.now(timezone.utc)
            with TinyDB(database_path) as db:
                db.insert(
                    {
                        "author": author,
                        "content": content,
                        "created_at": created_at.isoformat(),
                        "created_at_label": created_at.strftime("%Y-%m-%d %H:%M UTC"),
                    }
                )

        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
