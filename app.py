from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import re

app = Flask(__name__)

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["csv_file"]

    try:
       df = pd.read_csv(file)
    except Exception:
       return render_template("error.html")

    rows_before = len(df)
    columns_before = len(df.columns)

    duplicates_removed = 0
    empty_rows_removed = 0
    spaces_trimmed = "No"
    columns_standardized = "No"

    if request.form.get("remove_duplicates"):
        duplicates_removed = len(df[df.duplicated()])
        df = df.drop_duplicates()

    if request.form.get("remove_empty_rows"):
        empty_rows_removed = len(df[df.isnull().all(axis=1)])
        df = df.dropna(how="all")

    if request.form.get("trim_spaces"):
        for column in df.select_dtypes(include="object").columns:
            df[column] = df[column].str.strip()
        spaces_trimmed = "Yes"

    if request.form.get("standardize_columns"):
        cleaned_columns = []
        for col in df.columns:
            col = col.strip().lower()
            col = re.sub(r"\s+", "_", col)
            col = re.sub(r"[^a-z0-9_]", "", col)
            cleaned_columns.append(col)

        df.columns = cleaned_columns
        columns_standardized = "Yes"

    rows_after = len(df)
    columns_after = len(df.columns)

    cleaned_file_path = os.path.join(OUTPUT_FOLDER, "cleaned_file.csv")
    df.to_csv(cleaned_file_path, index=False)

    preview_table = df.head().to_html(classes="preview-table", index=False)

    return render_template(
        "results.html",
        rows_before=rows_before,
        rows_after=rows_after,
        columns_before=columns_before,
        columns_after=columns_after,
        duplicates_removed=duplicates_removed,
        empty_rows_removed=empty_rows_removed,
        spaces_trimmed=spaces_trimmed,
        columns_standardized=columns_standardized,
        preview_table=preview_table
    )

@app.route("/download")
def download():
    cleaned_file_path = os.path.join(OUTPUT_FOLDER, "cleaned_file.csv")
    return send_file(cleaned_file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)