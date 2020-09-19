# Youtube Condensed Audio
Create condensed audio files from YouTube videos and playlists with subtitles.

# Condensed Audio
If you have no idea what condensed audio is and how useful it is for language learning, please take a look at [this video](https://www.youtube.com/watch?v=QOLTeO-uCYU) by Matt vs. Japan.
**"Youtube Condensed Audio"** is a tool that'll simplyfy the process of creating condensed audio from youtube by using the subtitles that are present in the YouTube videos.

![img](https://imgur.com/RPmsqUA.png)

## Installation
* User
  * Download and extract the archive from the release.
  * Check the **Usage** section below for usage info.
* Developer
  * Download and extract the ZIP or Clone repository
  ```sh
    git clone https://github.com/the-bose/youtube-condensed-audio/
  ```
  * Install dependencies
  ```sh
    pip install -r requirements.txt
  ```

## Usage
* Configure the "config.txt"
  * **link** - Link to the YouTube video/playlist.
  * **exclude_no_sub** - (true/false) Neglects/Downloads videos with no subs.
  * **speed** - Speed of the final condensed audio (1.00 = Normal Speed).
* Run "app.py"
```sh
  python app.py
```
* Find the condensed audio ```mp3``` file in the same folder as "app.py"
