import threading
import unittest
from url_crawler import crawl_page, request_page_url

from mock import patch
from bs4 import BeautifulSoup


class TestURLCrawler(unittest.TestCase):

    # Test request_page_url: extract all links from html page of a get request.
    @patch('requests.get')
    def test_request_page_url(self, mock_get):
        # Setup mock html content for get request return value.
        get_response = """<html><head><title>Example Title</title></head>
        <body>
        <p class="example"> testing testing
        <a href="#intro">About</a>,
        <a href="#work">Work</a>
        <a class="example" href="http://example.com" id="link1">Example</a> and
        <a class ="icon"></a>
        <a href="http://example2.com"></a>
        Testing testing.</p>
        <p class="story">...</p> </body></html>
        """
        mock_get.return_value.content = get_response

        # All links from html page.
        expected_result = [BeautifulSoup('''<a href="#intro">About</a>''', 'html.parser').a,
                           BeautifulSoup('''<a href="#work">Work</a>''', 'html.parser').a,
                           BeautifulSoup(
                               '<a class="example" href="http://example.com" id="link1">Example</a>',
                               'html.parser').a,
                           BeautifulSoup('''<a class ="icon" ></a>''', 'html.parser').a,
                           BeautifulSoup('''<a href="http://example2.com" ></a>''', 'html.parser').a]

        self.assertEqual(expected_result, request_page_url("http://test_url"))

    # Test crawl_page: Test that only valid links are returned and printed.
    @patch('url_crawler.request_page_url')
    def test_crawl_page(self, mock_request_page_url):
        # Setup mock for mock_request_page_url.
        # Includes links that are href, non-href, and href with and without 'http'.
        mock_request_page_url.return_value = [BeautifulSoup('''<a href="#intro">About</a>''', 'html.parser').a,
                                              BeautifulSoup('''<a href="#work">Work</a>''', 'html.parser').a,
                                              BeautifulSoup(
                                                  '<a class="example" href="http://example.com" id="link1">Example</a>',
                                                  'html.parser').a,
                                              BeautifulSoup('''<a class ="icon" >''', 'html.parser').a,
                                              BeautifulSoup('''<a href="http://example2.com" >''', 'html.parser').a]

        # Expected results include only href links that start with http.
        expected_result = ["http://example.com", "http://example2.com"]

        # Start testing thread and add results to `actual_results`.
        actual_results = []
        new_thread = threading.Thread(actual_results.extend(crawl_page("https://test")))
        new_thread.start()
        new_thread.join()

        self.assertEqual(expected_result, actual_results)


if __name__ == '__main__':
    unittest.main()
