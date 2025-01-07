from flask import Flask, request, redirect, url_for, jsonify
import yt_dlp

app = Flask(__name__)

# Function to process the submitted input
def process_input(user_input):
    video_url = user_input

    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        ydl_opts = {
            'format': 'best',  # This ensures only the best video format is selected
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)

        video_formats = []
        audio_formats = []

        for fmt in video_info.get("formats", []):
            url = fmt.get("url")
            file_size_mb = fmt.get("filesize", 0) / (1024 * 1024)  # Convert to MBs
            if url and url.startswith("https://rr"):
                if fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
                    video_formats.append({
                        "format_id": fmt.get("format_id"),
                        "format_note": fmt.get("format_note"),
                        "ext": fmt.get("ext"),
                        "url": url,
                        "file_size_mb": round(file_size_mb, 2)
                    })
                elif fmt.get("acodec") != "none" and fmt.get("vcodec") == "none":
                    audio_formats.append({
                        "format_id": fmt.get("format_id"),
                        "format_note": fmt.get("abr"),
                        "ext": fmt.get("ext"),
                        "url": url,
                        "file_size_mb": round(file_size_mb, 2)
                    })

        # Keep only the lowest 3 abr audio formats
        audio_formats = sorted(audio_formats, key=lambda x: x.get("abr", float('inf')))[:3]

        video_details = {
            "title": video_info.get("title"),
            "thumbnail": video_info.get("thumbnail"),
            "uploader": video_info.get("uploader"),
            "duration": video_info.get("duration"),
            "video_formats": video_formats,
            "audio_formats": audio_formats
        }

        return generate_video_details_page(video_details), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
#Generate html

def generate_video_details_page(video_details):
    title = video_details.get("title", "Unknown Title")
    thumbnail = video_details.get("thumbnail", "")
    uploader = video_details.get("uploader", "Unknown Uploader")
    duration = video_details.get("duration", "Unknown Duration")
    audio_formats = video_details.get("audio_formats", [])
    video_formats = video_details.get("video_formats", [])

    # HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <title>{title}</title>
    <style>
        body{{
        padding: 0 1em;
            font-family: "Courier New", Courier, monospace;
            background-color: #000;
            color: rgb(250, 250, 250);
            font-size: 1em;
            max-width: 700px;
            margin: auto;
          }}
          header
          {{padding: 0.5em 1.5em;
          
            background-color: black;}}
            
          header,h1{{
            position: sticky;
            top: 0;
            color: red;
			text-align: center;
			margin: 0;
          }}
          h2,h3{{
            color: red;
			text-align: center;
            margin: 0.2em;
            margin-bottom: 0;
          }}
          em,blockquote{{
            color: aliceblue;
          }}
          
          .img {{
          width: 50%;
		  display: flex;
		  justify-content: center;
		  margin: 1px auto;
		  }}
		  
		  img{{
          width: 100%;
            object-fit: cover;
		  }}
          ul{{
          margin: 0.2em;
          }}
          hr{{
            border: 1px dashed red;
          }}
          footer{{height: 3rem;
            text-align: center;
            font-size: 0.9em;
          }}
          a:link{{
            color: limered;
            text-decoration: none;
          }}
          a:hover{{
            color: lime;
          }}
          a:active{{
            color: red;
          }}
          p{{
          margin: 0.5em;
          }}
		  .linkbox{{
		  display: flex;
		  justify-content: center;
		  flex-direction: column;
		  }}
		  .link{{
		  display: flex;
		  justify-content: space-between;
		  border: solid gray 1px;
		  padding: 1px 15px;
		  margin: 5px 0px;
		  }}
		  .link > a{{
          width:10%;
		  display: flex;
		  justify-content: center;
          text-decoration: none;
		  }}
		  .blink > a{{
          width: 100%;
		  display: flex;
		  justify-content: center;
          text-decoration: none;
          color: white;
		  }}
		  .blink{{
		  display: flex;
		  justify-content: center;
		  border: solid green 1px;
		  background-color: green;
		  padding: 1px 15px;
		  margin: 5px 0px;
		  }}
		  .btn{{
		  align-self: center;
		  }}
		  .dbtn{{
          color: green;
		  }}
    </style>
    </head>
    <body>
        <header>
            <h1>YouTube Video Downloader</h1>
        </header>
        <div class="img">
            <img src="{thumbnail}" alt="Thumbnail" class="thumbnail">
        </div>
        <h3>Video Details</h3>
        <ul>
            <li>Title: {title}</li>
            <li>Uploader: {uploader}</li>
            <li>Duration: {duration} seconds</li>
        </ul>
        <h3>Links</h3>
        <div class="linkbox">
            {"".join([f'''
                        <div class="link">
                        <p><i class="fa fa-music btn" aria-hidden="true"></i> MP3 ({round(fmt.get("format_note", 0))} Kbps) {round(fmt.get("file_size_mb", 0))} MB</p>
                        <a href="{fmt.get("url", "Unknown")}" target="_blank"> <i class="fa fa-download btn dbtn"></i></a>
                        </div>
                    ''' for fmt in audio_formats])}
                    
            {"".join([f'''
                        <div class="link">
                        <p><i class="fa fa-video-camera btn" aria-hidden="true"></i> MP4 ({fmt.get("format_note", "Unknown")}) {round(fmt.get("file_size_mb", 0))} MB</p>
                        <a href="{fmt.get("url", "Unknown")}" target="_blank"> <i class="fa fa-download btn dbtn"></i></a>
                        </div>
                    ''' for fmt in video_formats])}
            <div class="blink">
                <a href="/"><p><i class="fa fa-home btn" aria-hidden="true"></i> Home</p></a>
            </div>
        </div>
        <br>
        <br>
        <footer>
            <hr>
            <p>©Neeraj Pratap Singh | 2024</a></p>
        </footer>
    </body>

    <script>
    function downloadFile(url, filename) {{
        fetch(url)
            .then(response => response.blob())
            .then(blob => {{
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                link.remove();
            }})
            .catch(err => console.error('Download failed:', err));
    }}
    </script>
    </html>

    """
    return html_content


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        result_html = process_input(user_input)
        return result_html
    
    # Serve the home page HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <title>YouTube Video Downloader</title>
    <style>
            body{
            max-width:700px;
            padding: 0 1em;
            padding-top: 0;
            font-family: "Courier New", Courier, monospace;
            background-color: #000;
            color: rgb(250, 250, 250);
            font-size: 1em;
            margin: auto;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            text-align: center;
            min-height:100vh;
          }
          
          header
          {padding: 0.5em 1.5em;
            background-color: black;
          }
          header,h1{
            position: sticky;
            top: 0;
            color: red;
			text-align: center;
			margin: 0;
          }
          .container{
          display: flex;
          flex-direction: column;
          justify-content: center;
          margin: auto;
          }
            input[type="text"] {
                font-family: "Courier New", Courier, monospace;
                font-size: 1em;
                padding: 10px; 
                width: 260px; 
                border: 1px;
                border-radius: 5px;
                outline:none
            }
            button { 
                font-family: "Courier New", Courier, monospace;
                font-size: 1em;
                width: 100px; 
                padding: 11px 11px; 
                margin: 15px 0px; 
                background-color: green; 
                color: white; 
                border: none; 
                cursor: pointer; 
                border-radius: 25px;
            }
            button:hover { 
                background-color: #45a049; 
            }
            hr{
            width:100%;
            border: 1px dashed red;
            }
            p{
            margin: 0.5em;
            }
            footer{
          height: 3rem; 
            text-align: center;
            font-size: 0.9em;
            }
        </style>
    </head>
    <body>
    <header>
            <h1>YouTube Video Downloader</h1>
    </header>
    <div class= "container">
        <h3>Enter Video URL</h3>
        <form method="POST">
            <input type="text" name="user_input" placeholder="https://..." required>
            <button type="submit">Submit</i></button>
        </form>
    </div>
    <footer>
            <hr>
            <p>©Neeraj Pratap Singh | 2024</a></p>
    </footer>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0')
