#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウェブサイト診断ツール - 初心者向け説明付きバージョン
SEO、セキュリティ、パフォーマンス、アクセシビリティを診断
各項目にわかりやすい説明を追加
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse, urljoin
import ssl
import socket
from datetime import datetime
import json
import re
from collections import Counter

class WebsiteDiagnosisTool:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'seo': {},
            'security': {},
            'performance': {},
            'accessibility': {},
            'overall_score': 0
        }
        
        # 初心者向け説明
        self.explanations = self._get_explanations()
        
    def _get_explanations(self):
        """各診断項目のわかりやすい説明"""
        return {
            'seo': {
                'title': {
                    'what': 'タイトルタグは、ブラウザのタブやGoogle検索結果に表示される「ページのタイトル」です。',
                    'why': 'わかりやすいタイトルがあると、検索結果でクリックされやすくなります。',
                    'how': 'タイトルは30〜60文字が最適です。会社名やページの内容を簡潔に書きましょう。'
                },
                'meta_description': {
                    'what': 'メタディスクリプションは、Google検索結果でタイトルの下に表示される「説明文」です。',
                    'why': '魅力的な説明文があると、検索結果からのアクセスが増えます。',
                    'how': '120〜160文字で、ページの内容を簡潔に説明しましょう。'
                },
                'h1': {
                    'what': 'H1タグは、ページの「大見出し」です。新聞の1面の大きな見出しのようなものです。',
                    'why': 'Googleがページの内容を理解するための重要な手がかりになります。',
                    'how': 'H1タグは1ページに1つだけ配置し、ページの内容を表す見出しにしましょう。'
                },
                'alt': {
                    'what': 'alt属性は、画像の「説明文」です。画像が表示されない時や、目の不自由な方のために使われます。',
                    'why': 'Googleは画像の内容を理解できないので、alt属性で説明する必要があります。',
                    'how': '各画像に「何の画像か」を簡潔に説明する文章を付けましょう。'
                }
            },
            'security': {
                'https': {
                    'what': 'HTTPSは、ウェブサイトとの通信を「暗号化」する技術です。南京錠のマークが表示されます。',
                    'why': 'HTTPSがないと、入力した情報（パスワードやクレジットカード番号など）が盗まれる危険があります。',
                    'how': 'サーバー会社に「SSL証明書」を申請してインストールする必要があります（多くは無料）。',
                    'risk': '【危険度：高】HTTPSがないサイトは、Googleが「安全でない」と警告を表示します。'
                },
                'strict_transport_security': {
                    'what': 'HSTS（HTTP Strict Transport Security）は、「必ずHTTPSで接続する」という指示です。',
                    'why': '悪意のある人が、HTTPSをHTTPに変えて情報を盗む攻撃を防ぎます。',
                    'how': 'サーバーの設定で「Strict-Transport-Security」ヘッダーを追加します。',
                    'risk': '【危険度：中】HTTPSを使っていても、この設定がないと一部の攻撃を防げません。'
                },
                'x_frame_options': {
                    'what': 'X-Frame-Optionsは、「他のサイトに埋め込まれるのを防ぐ」設定です。',
                    'why': '悪意のあるサイトがあなたのサイトを埋め込んで、ユーザーを騙す攻撃（クリックジャッキング）を防ぎます。',
                    'how': 'サーバーの設定で「X-Frame-Options: DENY」または「SAMEORIGIN」を追加します。',
                    'risk': '【危険度：中】この設定がないと、偽のログイン画面などに悪用される可能性があります。'
                },
                'content_security_policy': {
                    'what': 'CSP（Content Security Policy）は、「どこからスクリプトを読み込むか」を制限する設定です。',
                    'why': '悪意のあるスクリプトが勝手に実行されるのを防ぎます（XSS攻撃対策）。',
                    'how': 'サーバーの設定で「Content-Security-Policy」ヘッダーを追加します。',
                    'risk': '【危険度：中〜高】この設定がないと、サイトに不正なコードを埋め込まれる危険があります。'
                }
            },
            'performance': {
                'load_time': {
                    'what': 'ページ読み込み時間は、サイトが表示されるまでにかかる時間です。',
                    'why': '読み込みが遅いと、ユーザーが待ちきれずに離脱してしまいます（3秒以上で半数が離脱）。',
                    'how': '画像を圧縮する、不要なスクリプトを削除する、サーバーを高速化するなどの方法があります。'
                },
                'page_size': {
                    'what': 'ページサイズは、ウェブページ全体のデータ量（MB）です。',
                    'why': 'ページサイズが大きいと、読み込みに時間がかかり、スマホのデータ通信量も増えます。',
                    'how': '画像を圧縮する、不要なコードを削除する、動画は外部サービスを使うなど。'
                },
                'compression': {
                    'what': '圧縮は、データを「zip形式」のように小さくして送る技術です。',
                    'why': '圧縮すると、データ量が50〜70%減少し、読み込みが速くなります。',
                    'how': 'サーバーの設定で「Gzip圧縮」または「Brotli圧縮」を有効にします。'
                }
            },
            'accessibility': {
                'lang': {
                    'what': 'lang属性は、「このページは何語で書かれているか」を示すものです。',
                    'why': '目の不自由な方が使う「読み上げソフト」が、正しい発音で読み上げるために必要です。',
                    'how': 'HTMLの最初に <html lang="ja"> のように言語を指定します（日本語は"ja"）。'
                },
                'main_landmark': {
                    'what': 'mainランドマークは、「ページのメインコンテンツはここ」という目印です。',
                    'why': '目の不自由な方が、読み上げソフトで「本文にジャンプ」できるようになります。',
                    'how': 'メインコンテンツを <main> タグで囲みます。'
                }
            }
        }
    
    def diagnose(self):
        """全ての診断を実行（エイリアス）"""
        return self.run_diagnosis()
    
    def run_diagnosis(self):
        """全ての診断を実行（内部メソッド）"""
        print(f"🔍 診断開始: {self.url}\n")
        
        # ページの取得
        try:
            start_time = time.time()
            response = requests.get(self.url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            load_time = time.time() - start_time
            
            self.response = response
            self.soup = BeautifulSoup(response.content, 'html.parser')
            self.load_time = load_time
            
        except Exception as e:
            print(f"❌ エラー: ページの取得に失敗しました - {str(e)}")
            return None
        
        # 各診断の実行
        self.diagnose_seo()
        self.diagnose_security()
        self.diagnose_performance()
        self.diagnose_accessibility()
        
        # 総合スコアの計算
        self.calculate_overall_score()
        
        return self.results
    
    def diagnose_seo(self):
        """SEO診断"""
        print("📊 SEO診断中...")
        seo = {}
        issues = []
        success = []
        explanations = []
        score = 0
        
        # タイトルタグ
        title = self.soup.find('title')
        if title and title.string:
            title_text = title.string.strip()
            seo['title'] = title_text
            seo['title_length'] = len(title_text)
            if 30 <= len(title_text) <= 60:
                score += 15
                success.append(f"Title tag is configured ({len(title_text)} chars)")
            else:
                issues.append(f"Title length is not optimal (current: {len(title_text)} chars, recommended: 30-60 chars)")
                explanations.append({
                    'issue': 'Title length',
                    'explanation': self.explanations['seo']['title']
                })
        else:
            issues.append("Title tag not found")
            explanations.append({
                'issue': 'Title tag missing',
                'explanation': self.explanations['seo']['title']
            })
            seo['title'] = None
        
        # メタディスクリプション
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_text = meta_desc.get('content').strip()
            seo['meta_description'] = desc_text
            seo['meta_description_length'] = len(desc_text)
            if 120 <= len(desc_text) <= 160:
                score += 15
                success.append(f"Meta description is configured ({len(desc_text)} chars)")
            else:
                issues.append(f"Meta description length is not optimal (current: {len(desc_text)} chars, recommended: 120-160 chars)")
                explanations.append({
                    'issue': 'Meta description length',
                    'explanation': self.explanations['seo']['meta_description']
                })
        else:
            issues.append("Meta description not found")
            explanations.append({
                'issue': 'Meta description missing',
                'explanation': self.explanations['seo']['meta_description']
            })
            seo['meta_description'] = None
        
        # 見出しタグの分析
        headings = {f'h{i}': [] for i in range(1, 7)}
        for i in range(1, 7):
            tags = self.soup.find_all(f'h{i}')
            headings[f'h{i}'] = [tag.get_text().strip() for tag in tags]
        
        seo['headings'] = headings
        
        # H1タグのチェック
        h1_count = len(headings['h1'])
        if h1_count == 1:
            score += 10
            success.append("Single H1 tag found")
        elif h1_count == 0:
            issues.append("H1 tag not found")
            explanations.append({
                'issue': 'H1 tag missing',
                'explanation': self.explanations['seo']['h1']
            })
        else:
            issues.append(f"Multiple H1 tags found ({h1_count})")
            explanations.append({
                'issue': 'Multiple H1 tags',
                'explanation': self.explanations['seo']['h1']
            })
        
        # 見出し構造のチェック
        if headings['h2']:
            score += 5
        else:
            issues.append("H2 tag not found")
        
        # 画像のalt属性チェック
        images = self.soup.find_all('img')
        total_images = len(images)
        images_with_alt = sum(1 for img in images if img.get('alt'))
        
        seo['total_images'] = total_images
        seo['images_with_alt'] = images_with_alt
        
        if total_images > 0:
            alt_ratio = images_with_alt / total_images
            if alt_ratio >= 0.9:
                score += 15
                success.append(f"Most images have alt attributes ({images_with_alt}/{total_images})")
            elif alt_ratio >= 0.7:
                score += 10
                issues.append(f"Some images missing alt attributes ({images_with_alt}/{total_images})")
                explanations.append({
                    'issue': 'Missing alt attributes',
                    'explanation': self.explanations['seo']['alt']
                })
            else:
                issues.append(f"Many images missing alt attributes ({images_with_alt}/{total_images})")
                explanations.append({
                    'issue': 'Missing alt attributes',
                    'explanation': self.explanations['seo']['alt']
                })
        
        # Open Graphタグ
        og_tags = {}
        for og in self.soup.find_all('meta', property=re.compile(r'^og:')):
            og_tags[og.get('property')] = og.get('content')
        seo['open_graph'] = og_tags
        if og_tags:
            score += 10
            success.append("Open Graph tags configured")
        
        # Twitter Cardタグ
        twitter_tags = {}
        for twitter in self.soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            twitter_tags[twitter.get('name')] = twitter.get('content')
        seo['twitter_card'] = twitter_tags
        if twitter_tags:
            score += 5
            success.append("Twitter Card tags configured")
        
        # Canonicalタグ
        canonical = self.soup.find('link', rel='canonical')
        seo['canonical'] = canonical.get('href') if canonical else None
        if canonical:
            score += 5
            success.append("Canonical tag configured")
        
        # 内部リンク数
        internal_links = []
        external_links = []
        for link in self.soup.find_all('a', href=True):
            href = link.get('href')
            if href.startswith('http'):
                if self.domain in href:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(href)
        
        seo['internal_links_count'] = len(internal_links)
        seo['external_links_count'] = len(external_links)
        
        if len(internal_links) > 0:
            score += 5
            success.append(f"Internal links found ({len(internal_links)})")
        
        # 構造化データ
        structured_data = []
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except:
                pass
        seo['structured_data'] = structured_data
        if structured_data:
            score += 10
            success.append("Structured data found")
        
        seo['score'] = min(score, 100)
        seo['issues'] = issues
        seo['success'] = success
        seo['explanations'] = explanations
        self.results['seo'] = seo
        print(f"  ✅ SEOスコア: {seo['score']}/100")
    
    def diagnose_security(self):
        """セキュリティ診断"""
        print("🔒 セキュリティ診断中...")
        security = {}
        issues = []
        success = []
        explanations = []
        score = 0
        
        # HTTPS使用確認
        is_https = self.parsed_url.scheme == 'https'
        security['https'] = is_https
        if is_https:
            score += 30
            success.append("HTTPS enabled")
        else:
            issues.append("HTTPS not enabled (security risk)")
            explanations.append({
                'issue': 'HTTPS not enabled',
                'explanation': self.explanations['security']['https']
            })
        
        # セキュリティヘッダーのチェック
        headers = self.response.headers
        security_headers = {
            'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
            'X-Frame-Options': headers.get('X-Frame-Options'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
            'X-XSS-Protection': headers.get('X-XSS-Protection'),
            'Content-Security-Policy': headers.get('Content-Security-Policy'),
            'Referrer-Policy': headers.get('Referrer-Policy'),
            'Permissions-Policy': headers.get('Permissions-Policy')
        }
        
        security['security_headers'] = security_headers
        
        # 各ヘッダーのスコアリング
        header_scores = {
            'Strict-Transport-Security': 15,
            'X-Frame-Options': 10,
            'X-Content-Type-Options': 10,
            'X-XSS-Protection': 5,
            'Content-Security-Policy': 20,
            'Referrer-Policy': 5,
            'Permissions-Policy': 5
        }
        
        header_explanations = {
            'Strict-Transport-Security': self.explanations['security']['strict_transport_security'],
            'X-Frame-Options': self.explanations['security']['x_frame_options'],
            'Content-Security-Policy': self.explanations['security']['content_security_policy']
        }
        
        for header, value in security_headers.items():
            if value:
                score += header_scores.get(header, 0)
                success.append(f"{header} header configured")
            else:
                issues.append(f"{header} header not set")
                if header in header_explanations:
                    explanations.append({
                        'issue': f'{header} missing',
                        'explanation': header_explanations[header]
                    })
        
        # SSL証明書の確認（HTTPSの場合）
        if is_https:
            try:
                context = ssl.create_default_context()
                with socket.create_connection((self.domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                        cert = ssock.getpeercert()
                        security['ssl_certificate'] = {
                            'issued_to': cert.get('subject', []),
                            'issued_by': cert.get('issuer', []),
                            'valid_from': cert.get('notBefore'),
                            'valid_until': cert.get('notAfter')
                        }
                        success.append("Valid SSL certificate")
            except Exception as e:
                issues.append(f"SSL certificate check failed: {str(e)}")
                security['ssl_certificate'] = None
        
        security['score'] = min(score, 100)
        security['issues'] = issues
        security['success'] = success
        security['explanations'] = explanations
        self.results['security'] = security
        print(f"  ✅ セキュリティスコア: {security['score']}/100")
    
    def diagnose_performance(self):
        """パフォーマンス診断"""
        print("⚡ パフォーマンス診断中...")
        performance = {}
        issues = []
        success = []
        explanations = []
        score = 0
        
        # ページ読み込み時間
        performance['load_time'] = round(self.load_time, 3)
        if self.load_time < 1:
            score += 30
            success.append(f"Fast page load time ({round(self.load_time, 2)}s)")
        elif self.load_time < 2:
            score += 20
            issues.append(f"Page load time is slightly slow ({round(self.load_time, 2)}s)")
            explanations.append({
                'issue': 'Slow load time',
                'explanation': self.explanations['performance']['load_time']
            })
        elif self.load_time < 3:
            score += 10
            issues.append(f"Page load time is slow ({round(self.load_time, 2)}s)")
            explanations.append({
                'issue': 'Slow load time',
                'explanation': self.explanations['performance']['load_time']
            })
        else:
            issues.append(f"Page load time is very slow ({round(self.load_time, 2)}s)")
            explanations.append({
                'issue': 'Very slow load time',
                'explanation': self.explanations['performance']['load_time']
            })
        
        # ページサイズ
        page_size = len(self.response.content)
        performance['page_size_bytes'] = page_size
        performance['page_size_kb'] = round(page_size / 1024, 2)
        
        if page_size < 500 * 1024:
            score += 20
            success.append(f"Appropriate page size ({round(page_size/1024, 2)}KB)")
        elif page_size < 1024 * 1024:
            score += 15
            issues.append(f"Page size is slightly large ({round(page_size/1024, 2)}KB)")
            explanations.append({
                'issue': 'Large page size',
                'explanation': self.explanations['performance']['page_size']
            })
        elif page_size < 3 * 1024 * 1024:
            score += 5
            issues.append(f"Page size is large ({round(page_size/1024/1024, 2)}MB)")
            explanations.append({
                'issue': 'Large page size',
                'explanation': self.explanations['performance']['page_size']
            })
        else:
            issues.append(f"Page size is very large ({round(page_size/1024/1024, 2)}MB)")
            explanations.append({
                'issue': 'Very large page size',
                'explanation': self.explanations['performance']['page_size']
            })
        
        # リソース数のカウント
        resources = {
            'scripts': len(self.soup.find_all('script')),
            'stylesheets': len(self.soup.find_all('link', rel='stylesheet')),
            'images': len(self.soup.find_all('img')),
            'iframes': len(self.soup.find_all('iframe'))
        }
        performance['resources'] = resources
        
        total_resources = sum(resources.values())
        if total_resources < 30:
            score += 15
            success.append(f"Appropriate number of resources ({total_resources})")
        elif total_resources < 50:
            score += 10
            success.append(f"Moderate number of resources ({total_resources})")
        else:
            issues.append(f"Too many resources (total: {total_resources})")
        
        # 圧縮の確認
        content_encoding = self.response.headers.get('Content-Encoding')
        performance['compression'] = content_encoding
        if content_encoding in ['gzip', 'br', 'deflate']:
            score += 15
            success.append(f"Content compression enabled ({content_encoding})")
        else:
            issues.append("Content compression not enabled")
            explanations.append({
                'issue': 'No compression',
                'explanation': self.explanations['performance']['compression']
            })
        
        # キャッシュ制御
        cache_control = self.response.headers.get('Cache-Control')
        performance['cache_control'] = cache_control
        if cache_control:
            score += 10
            success.append("Cache-Control header configured")
        else:
            issues.append("Cache-Control header not set")
        
        performance['score'] = min(score, 100)
        performance['issues'] = issues
        performance['success'] = success
        performance['explanations'] = explanations
        self.results['performance'] = performance
        print(f"  ✅ パフォーマンススコア: {performance['score']}/100")
    
    def diagnose_accessibility(self):
        """アクセシビリティ診断"""
        print("♿ アクセシビリティ診断中...")
        accessibility = {}
        issues = []
        success = []
        explanations = []
        score = 0
        
        # 言語属性
        html_tag = self.soup.find('html')
        lang = html_tag.get('lang') if html_tag else None
        accessibility['lang_attribute'] = lang
        if lang:
            score += 15
            success.append(f"HTML lang attribute present ({lang})")
        else:
            issues.append("HTML element missing lang attribute")
            explanations.append({
                'issue': 'Missing lang attribute',
                'explanation': self.explanations['accessibility']['lang']
            })
        
        # 画像のalt属性
        images = self.soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        accessibility['images_without_alt_count'] = len(images_without_alt)
        
        if len(images) > 0:
            alt_ratio = (len(images) - len(images_without_alt)) / len(images)
            if alt_ratio == 1:
                score += 20
                success.append("All images have alt attributes")
            elif alt_ratio >= 0.8:
                score += 15
                issues.append(f"{len(images_without_alt)} images missing alt attributes")
            else:
                issues.append(f"Many images missing alt attributes ({len(images_without_alt)}/{len(images)})")
        
        # フォームラベル
        inputs = self.soup.find_all(['input', 'textarea', 'select'])
        inputs_with_labels = 0
        for inp in inputs:
            inp_id = inp.get('id')
            aria_label = inp.get('aria-label')
            if inp_id and self.soup.find('label', attrs={'for': inp_id}):
                inputs_with_labels += 1
            elif aria_label:
                inputs_with_labels += 1
        
        accessibility['form_inputs_count'] = len(inputs)
        accessibility['inputs_with_labels'] = inputs_with_labels
        
        if len(inputs) > 0:
            if inputs_with_labels == len(inputs):
                score += 15
                success.append("All form elements have labels")
            elif inputs_with_labels >= len(inputs) * 0.7:
                score += 10
                issues.append(f"Some form elements missing labels ({inputs_with_labels}/{len(inputs)})")
            else:
                issues.append(f"Many form elements missing labels ({inputs_with_labels}/{len(inputs)})")
        
        # ARIA属性の使用
        aria_elements = self.soup.find_all(attrs={'role': True})
        aria_labels = self.soup.find_all(attrs={'aria-label': True})
        accessibility['aria_roles_count'] = len(aria_elements)
        accessibility['aria_labels_count'] = len(aria_labels)
        
        if len(aria_elements) > 0 or len(aria_labels) > 0:
            score += 10
            success.append(f"ARIA attributes used ({len(aria_elements)} roles, {len(aria_labels)} labels)")
        
        # ランドマーク要素
        landmarks = ['header', 'nav', 'main', 'footer', 'aside', 'section', 'article']
        found_landmarks = {tag: len(self.soup.find_all(tag)) for tag in landmarks}
        accessibility['landmarks'] = found_landmarks
        
        if found_landmarks['main'] > 0:
            score += 10
            success.append("Main landmark found")
        else:
            issues.append("Main landmark not found")
            explanations.append({
                'issue': 'Missing main landmark',
                'explanation': self.explanations['accessibility']['main_landmark']
            })
        
        if found_landmarks['nav'] > 0:
            score += 5
            success.append("Navigation landmark found")
        
        # 見出しの階層構造
        headings_order = []
        for i in range(1, 7):
            for tag in self.soup.find_all(f'h{i}'):
                headings_order.append(i)
        
        heading_skip = False
        for i in range(len(headings_order) - 1):
            if headings_order[i+1] - headings_order[i] > 1:
                heading_skip = True
                break
        
        if not heading_skip and len(headings_order) > 0:
            score += 10
            success.append("Proper heading hierarchy")
        elif heading_skip:
            issues.append("Heading hierarchy issues (e.g., h4 after h2)")
        
        # リンクテキストのチェック
        links = self.soup.find_all('a')
        empty_links = [link for link in links if not link.get_text().strip() and not link.get('aria-label')]
        accessibility['empty_links_count'] = len(empty_links)
        
        if len(empty_links) == 0 and len(links) > 0:
            score += 10
            success.append("All links have text")
        elif len(empty_links) > 0:
            issues.append(f"{len(empty_links)} links without text")
        
        accessibility['score'] = min(score, 100)
        accessibility['issues'] = issues
        accessibility['success'] = success
        accessibility['explanations'] = explanations
        self.results['accessibility'] = accessibility
        print(f"  ✅ アクセシビリティスコア: {accessibility['score']}/100")
    
    def calculate_overall_score(self):
        """総合スコアの計算"""
        weights = {
            'seo': 0.3,
            'security': 0.3,
            'performance': 0.2,
            'accessibility': 0.2
        }
        
        overall = 0
        for category, weight in weights.items():
            overall += self.results[category]['score'] * weight
        
        self.results['overall_score'] = round(overall, 1)
        
        # Streamlitアプリ用に scores キーを追加
        self.results['scores'] = {
            'seo': self.results['seo']['score'],
            'security': self.results['security']['score'],
            'performance': self.results['performance']['score'],
            'accessibility': self.results['accessibility']['score']
        }
        
        print(f"\n🎯 総合スコア: {self.results['overall_score']}/100")


def main():
    """メイン関数"""
    print("=" * 80)
    print("🔍 ウェブサイト診断ツール（説明付きバージョン）")
    print("=" * 80)
    print("")
    
    url = input("診断するURLを入力してください: ").strip()
    
    if not url:
        print("❌ URLが入力されていません")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print("")
    
    tool = WebsiteDiagnosisTool(url)
    results = tool.run_diagnosis()
    
    if results:
        # 説明付きレポートを出力
        print("\n" + "=" * 80)
        print("📋 診断レポート（詳細説明付き）")
        print("=" * 80)
        
        for category in ['seo', 'security', 'performance', 'accessibility']:
            data = results[category]
            if data.get('explanations'):
                print(f"\n【{category.upper()}】")
                for exp in data['explanations']:
                    print(f"\n⚠️ {exp['issue']}")
                    print(f"  📝 {exp['explanation']['what']}")
                    print(f"  💡 {exp['explanation']['why']}")
                    print(f"  🔧 {exp['explanation']['how']}")
                    if 'risk' in exp['explanation']:
                        print(f"  ⚠️ {exp['explanation']['risk']}")
        
        # 結果をJSONファイルに保存
        output_file = f"diagnosis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n💾 詳細な診断結果を {output_file} に保存しました")


if __name__ == "__main__":
    main()
