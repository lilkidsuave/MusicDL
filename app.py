import os
import requests
import tempfile
from flask import Flask, request, render_template, redirect, url_for, flash
from urllib.parse import quote as url_quote
import argparse
from orpheus.core import *
from orpheus.music_downloader import beauty_format_seconds

app = Flask(__name__)
app.secret_key = 'your_secret_key'

services = ["qobuz", "service2", "service3"]  # Replace with actual service names



def run_orpheus(arguments):
    parser = argparse.ArgumentParser(description='Orpheus: modular music archival')
    parser.add_argument('-p', '--private', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-o', '--output', help='Select a download output path. Default is the provided download path in config/settings.py')
    parser.add_argument('-lr', '--lyrics', default='default', help='Set module to get lyrics from')
    parser.add_argument('-cv', '--covers', default='default', help='Override module to get covers from')
    parser.add_argument('-cr', '--credits', default='default', help='Override module to get credits from')
    parser.add_argument('-sd', '--separatedownload', default='default', help='Select a different module that will download the playlist instead of the main module. Only for playlists.')
    parser.add_argument('arguments', nargs='*', help=argparse.SUPPRESS)
    args = parser.parse_args(arguments)

    orpheus = Orpheus(args.private)

    if not args.arguments:
        parser.print_help()
        return []

    orpheus_mode = args.arguments[0].lower()
    if orpheus_mode == 'search':
        if len(args.arguments) > 3:
            modulename = args.arguments[1].lower()
            if modulename in orpheus.module_list:
                try:
                    query_type = DownloadTypeEnum[args.arguments[2].lower()]
                except KeyError:
                    flash(f'{args.arguments[2].lower()} is not a valid search type!')
                    return []
                
                query = ' '.join(args.arguments[3:])
                module = orpheus.load_module(modulename)
                items = module.search(query_type, query, limit=orpheus.settings['global']['general']['search_limit'])
                
                if len(items) == 0:
                    flash(f'No search results for {query_type.name}: {query}')
                    return []
                
                results = []
                for index, item in enumerate(items, start=1):
                    additional_details = '[E] ' if item.explicit else ''
                    additional_details += f'[{beauty_format_seconds(item.duration)}] ' if item.duration else ''
                    additional_details += f'[{item.year}] ' if item.year else ''
                    additional_details += ' '.join([f'[{i}]' for i in item.additional]) if item.additional else ''
                    if query_type is not DownloadTypeEnum.artist:
                        artists = ', '.join(item.artists) if item.artists else ''
                        result = f'{str(index)}. {item.name} - {artists} {additional_details}'
                    else:
                        result = f'{str(index)}. {item.name} {additional_details}'
                    results.append((index, result, item))
                return results
            else:
                flash(f'Unknown module name "{modulename}".')
                return []
        else:
            flash('Search must be done as [search] [module] [track/artist/playlist/album] [query]')
            return []
    elif orpheus_mode == 'download':
        if len(args.arguments) > 2:
            modulename = args.arguments[1].lower()
            link = args.arguments[2]
            if modulename in orpheus.module_list:
                module = orpheus.load_module(modulename)
                # Ensure that the module has the appropriate method for downloading
                if hasattr(module, 'get_track_download'):
                    download_info = module.get_track_download(link)
                    # Download the file and save it to a temporary location
                    response = requests.get(download_info.file_url, stream=True)
                    temp_dir = tempfile.gettempdir()
                    temp_file = os.path.join(temp_dir, os.path.basename(link))
                    with open(temp_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return temp_file
                else:
                    flash(f'Module "{modulename}" does not support downloading.')
                    return []
            else:
                flash(f'Unknown module name "{modulename}".')
                return []
        else:
            flash('Download must be done as [download] [module] [link]')
            return []
    else:
        flash('Invalid mode.')
        return []

@app.route('/download', methods=['POST'])
def download():
    service = request.form['service']
    link = request.form['link']
    
    if service and link:
        args = ['download', service, link]
        results = run_orpheus(args)
        flash('Download started successfully.')
    else:
        flash('Please provide both service and link.')

    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        service = request.form['service']
        search_type = request.form['search_type']
        query = request.form['query']
        
        if service and search_type and query:
            args = ['search', service, search_type, query]
            results = run_orpheus(args)
            return render_template('index.html', services=services, results=results)
        else:
            flash('Please fill in all fields.')
    
    return render_template('index.html', services=services, results=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
