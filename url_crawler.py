import argparse
import signal
import sys
import threading
from queue import Queue
import requests
import requests.exceptions as re
from bs4 import BeautifulSoup

url_queue = Queue()
threads = []

# Lock used for printing url and url's children without interruption.
threadLock = threading.Lock()

# Event checked by threads to know when to terminate and cleanup.
exit_event = threading.Event()


def crawl_page(new_url):
    """
    Crawls html content of url to find all <a href> links that start with http.

    Prints out url and url's children to stdout.

    :param new_url: page to crawl for links (str)
    :return: returns list of new_links to crawl for (List of str)
    """
    # Check for thread signal termination.
    check_event()

    # Request contents of url and get all a tags.
    links = request_page_url(new_url)
    # Collect all valid href links that start with http.
    new_links = []

    for link in links:
        try:
            link = link.get('href')
            if link and link.startswith('http'):

                if link not in new_links:
                    new_links.append(link)

        except KeyError:
            # Not an href link.
            pass

    # Check for thread signal termination.
    check_event()

    print_links(new_links, new_url)

    return new_links


def request_page_url(new_url):
    """
    Requests url and gets all <a> links.

    :param new_url: URL to get and crawl for links.
    :return: list of all links
    """
    try:
        page = requests.get(new_url)
        # Use BeautifulSoup to parse page content into html

        soup = BeautifulSoup(page.content,
                             'html.parser',
                             from_encoding="iso-8859-1")
        # Find all <a> elements.
        links = soup.find_all('a')

    except re.MissingSchema:
        print("Error: invalid url")
        sys.exit(1)

    except:
        sys.exit(1)

    return links


def print_links(new_links, curr_url):
    """
    Prints out current link and its children.

    :param new_links: children links of curr_url (List of str)
    :param curr_url: crawled url (str)
    """
    # Lock then thread to print in correct order.
    threadLock.acquire()

    # Check for thread signal termination.
    check_event(threadLock)

    print(curr_url)
    for link in new_links:
        check_event(threadLock)
        print(" " + link)

    threadLock.release()


def check_event(lock=None):
    """
    Checks to see if `exit_event` was set in order to terminate thread.

    If a thread lock is passed in, it is released.

    :param lock: Lock to release (threading.Lock)
    """
    if exit_event.is_set():
        if lock:
            lock.release()
        sys.exit(0)


def signal_handler(signum, frame):
    """
    Sigint signal handler.

    Sets the exit_event used to terminate threads and waits for them all to
    join before exiting.
    """
    # Set exit event.
    exit_event.set()
    print(F'Cleaning up {threading.active_count()} threads...')

    # Get all threads that are still alive.
    running_threads = [thread for thread in threads if thread.is_alive()]

    for t in running_threads:
        t.join()

    sys.exit(0)


def append_list_to_q(new_list):
    """
    Helper function used to add new items to `url_queue`.

    :param new_list: list of new links to be added to queue (List of str)
    """
    for item in new_list:
        url_queue.put(item)


if __name__ == "__main__":

    # Setup signal handler for SIGINT.
    signal.signal(signal.SIGINT, signal_handler)

    # Setup command line parser.
    parser = argparse.ArgumentParser(description='URL CRAWLER')
    parser.add_argument('url', type=str, nargs=1,
                        help='URL to Crawl for links')
    args = parser.parse_args()
    url = args.url[0]

    url_queue.put(url)

    # Starts new url_crawler thread each iteration.
    while True and not exit_event.is_set():

        url = url_queue.get()

        # Starts new thread. Children of each url are returned upon
        # termination and added to url_queue.
        new_thread = threading.Thread(target=lambda q,
                                      arg1: append_list_to_q(crawl_page(url)),
                                      args=(url_queue, url))

        # Setup and start thread.
        threads.append(new_thread)
        new_thread.daemon = True
        new_thread.start()

        # Update threads so only alive ones are in list.
        threads.append(new_thread)

        # Wait for thread to finish if url_queue is empty.
        if url_queue.empty() and new_thread.is_alive():
            new_thread.join()

        # Exit loop if no more urls to crawl and no more active threads.
        if url_queue.empty() and threading.active_count() != 0:
            break

    sys.exit(0)
