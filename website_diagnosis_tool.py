#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウェブサイト診断ツール - 包括的な診断システム
SEO、セキュリティ、パフォーマンス、アクセシビリティを診断
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
        
    def run_diagnosis(self):
        """全ての診断を実行"""
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
        score = 0
        
        # タイトルタグ
        title = self.soup.find('title')
        if title and title.string:
            title_text = title.string.strip()
            seo['title'] = title_text
            seo['title_length'] = len(title_text)
            if 30 <= len(title_text) <= 60:
                score += 15
            else:
                issues.append(f"タイトルの長さが最適ではありません（現在: {len(title_text)}文字、推奨: 30-60文字）")
        else:
            issues.append("タイトルタグがありません")
            seo['title'] = None
        
        # メタディスクリプション
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_text = meta_desc.get('content').strip()
            seo['meta_description'] = desc_text
            seo['meta_description_length'] = len(desc_text)
            if 120 <= len(desc_text) <= 160:
                score += 15
            else:
                issues.append(f"メタディスクリプションの長さが最適ではありません（現在: {len(desc_text)}文字、推奨: 120-160文字）")
        else:
            issues.append("メタディスクリプションがありません")
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
        elif h1_count == 0:
            issues.append("H1タグがありません")
        else:
            issues.append(f"H1タグが複数あります（{h1_count}個）")
        
        # 見出し構造のチェック
        if headings['h2']:
            score += 5
        else:
            issues.append("H2タグがありません")
        
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
            elif alt_ratio >= 0.7:
                score += 10
                issues.append(f"一部の画像にalt属性がありません（{images_with_alt}/{total_images}）")
            else:
                issues.append(f"多くの画像にalt属性がありません（{images_with_alt}/{total_images}）")
        
        # メタキーワード（参考情報）
        meta_keywords = self.soup.find('meta', attrs={'name': 'keywords'})
        seo['meta_keywords'] = meta_keywords.get('content') if meta_keywords else None
        
        # Open Graphタグ
        og_tags = {}
        for og in self.soup.find_all('meta', property=re.compile(r'^og:')):
            og_tags[og.get('property')] = og.get('content')
        seo['open_graph'] = og_tags
        if og_tags:
            score += 10
        
        # Twitter Cardタグ
        twitter_tags = {}
        for twitter in self.soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            twitter_tags[twitter.get('name')] = twitter.get('content')
        seo['twitter_card'] = twitter_tags
        if twitter_tags:
            score += 5
        
        # Canonicalタグ
        canonical = self.soup.find('link', rel='canonical')
        seo['canonical'] = canonical.get('href') if canonical else None
        if canonical:
            score += 5
        
        # robotsメタタグ
        robots_meta = self.soup.find('meta', attrs={'name': 'robots'})
        seo['robots_meta'] = robots_meta.get('content') if robots_meta else None
        
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
        
        # 構造化データ（JSON-LD）
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
        
        seo['score'] = min(score, 100)
        seo['issues'] = issues
        self.results['seo'] = seo
        print(f"  ✅ SEOスコア: {seo['score']}/100")
    
    def diagnose_security(self):
        """セキュリティ診断"""
        print("🔒 セキュリティ診断中...")
        security = {}
        issues = []
        score = 0
        
        # HTTPS使用確認
        is_https = self.parsed_url.scheme == 'https'
        security['https'] = is_https
        if is_https:
            score += 30
        else:
            issues.append("HTTPSを使用していません（セキュリティリスク）")
        
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
        
        for header, value in security_headers.items():
            if value:
                score += header_scores.get(header, 0)
            else:
                issues.append(f"{header}ヘッダーが設定されていません")
        
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
            except Exception as e:
                issues.append(f"SSL証明書の確認に失敗: {str(e)}")
                security['ssl_certificate'] = None
        
        # Cookie設定の確認
        cookies = self.response.cookies
        security['cookies_count'] = len(cookies)
        secure_cookies = sum(1 for cookie in cookies if cookie.secure)
        httponly_cookies = sum(1 for cookie in cookies if cookie.has_nonstandard_attr('HttpOnly'))
        
        security['secure_cookies'] = secure_cookies
        security['httponly_cookies'] = httponly_cookies
        
        if len(cookies) > 0:
            if secure_cookies == len(cookies):
                score += 5
            if httponly_cookies > 0:
                score += 5
        
        security['score'] = min(score, 100)
        security['issues'] = issues
        self.results['security'] = security
        print(f"  ✅ セキュリティスコア: {security['score']}/100")
    
    def diagnose_performance(self):
        """パフォーマンス診断"""
        print("⚡ パフォーマンス診断中...")
        performance = {}
        issues = []
        score = 0
        
        # ページ読み込み時間
        performance['load_time'] = round(self.load_time, 3)
        if self.load_time < 1:
            score += 30
        elif self.load_time < 2:
            score += 20
            issues.append(f"ページ読み込み時間がやや遅いです（{round(self.load_time, 2)}秒）")
        elif self.load_time < 3:
            score += 10
            issues.append(f"ページ読み込み時間が遅いです（{round(self.load_time, 2)}秒）")
        else:
            issues.append(f"ページ読み込み時間が非常に遅いです（{round(self.load_time, 2)}秒）")
        
        # ページサイズ
        page_size = len(self.response.content)
        performance['page_size_bytes'] = page_size
        performance['page_size_kb'] = round(page_size / 1024, 2)
        
        if page_size < 500 * 1024:  # 500KB未満
            score += 20
        elif page_size < 1024 * 1024:  # 1MB未満
            score += 15
            issues.append(f"ページサイズがやや大きいです（{round(page_size/1024, 2)}KB）")
        elif page_size < 3 * 1024 * 1024:  # 3MB未満
            score += 5
            issues.append(f"ページサイズが大きいです（{round(page_size/1024/1024, 2)}MB）")
        else:
            issues.append(f"ページサイズが非常に大きいです（{round(page_size/1024/1024, 2)}MB）")
        
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
        elif total_resources < 50:
            score += 10
        else:
            issues.append(f"リソース数が多すぎます（合計: {total_resources}）")
        
        # 圧縮の確認
        content_encoding = self.response.headers.get('Content-Encoding')
        performance['compression'] = content_encoding
        if content_encoding in ['gzip', 'br', 'deflate']:
            score += 15
        else:
            issues.append("コンテンツ圧縮が使用されていません")
        
        # キャッシュ制御
        cache_control = self.response.headers.get('Cache-Control')
        performance['cache_control'] = cache_control
        if cache_control:
            score += 10
        else:
            issues.append("Cache-Controlヘッダーが設定されていません")
        
        # 画像の最適化チェック
        large_images = []
        for img in self.soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith('data:'):
                # 画像サイズのチェック（実際のダウンロードは省略）
                if src.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # 実装簡略化のため、警告のみ
                    pass
        
        # インラインスタイルの使用
        inline_styles = len(self.soup.find_all(style=True))
        performance['inline_styles_count'] = inline_styles
        if inline_styles > 10:
            issues.append(f"インラインスタイルが多用されています（{inline_styles}個）")
        
        performance['score'] = min(score, 100)
        performance['issues'] = issues
        self.results['performance'] = performance
        print(f"  ✅ パフォーマンススコア: {performance['score']}/100")
    
    def diagnose_accessibility(self):
        """アクセシビリティ診断"""
        print("♿ アクセシビリティ診断中...")
        accessibility = {}
        issues = []
        score = 0
        
        # 言語属性
        html_tag = self.soup.find('html')
        lang = html_tag.get('lang') if html_tag else None
        accessibility['lang_attribute'] = lang
        if lang:
            score += 15
        else:
            issues.append("HTML要素にlang属性がありません")
        
        # 画像のalt属性（再確認）
        images = self.soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        accessibility['images_without_alt_count'] = len(images_without_alt)
        
        if len(images) > 0:
            alt_ratio = (len(images) - len(images_without_alt)) / len(images)
            if alt_ratio == 1:
                score += 20
            elif alt_ratio >= 0.8:
                score += 15
                issues.append(f"{len(images_without_alt)}個の画像にalt属性がありません")
            else:
                issues.append(f"多くの画像にalt属性がありません（{len(images_without_alt)}/{len(images)}）")
        
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
            elif inputs_with_labels >= len(inputs) * 0.7:
                score += 10
                issues.append(f"一部のフォーム要素にラベルがありません（{inputs_with_labels}/{len(inputs)}）")
            else:
                issues.append(f"多くのフォーム要素にラベルがありません（{inputs_with_labels}/{len(inputs)}）")
        
        # ARIA属性の使用
        aria_elements = self.soup.find_all(attrs={'role': True})
        aria_labels = self.soup.find_all(attrs={'aria-label': True})
        accessibility['aria_roles_count'] = len(aria_elements)
        accessibility['aria_labels_count'] = len(aria_labels)
        
        if len(aria_elements) > 0 or len(aria_labels) > 0:
            score += 10
        
        # ランドマーク要素
        landmarks = ['header', 'nav', 'main', 'footer', 'aside', 'section', 'article']
        found_landmarks = {tag: len(self.soup.find_all(tag)) for tag in landmarks}
        accessibility['landmarks'] = found_landmarks
        
        if found_landmarks['main'] > 0:
            score += 10
        else:
            issues.append("mainランドマークがありません")
        
        if found_landmarks['nav'] > 0:
            score += 5
        
        # 見出しの階層構造
        headings_order = []
        for i in range(1, 7):
            for tag in self.soup.find_all(f'h{i}'):
                headings_order.append(i)
        
        # 見出しレベルの飛ばしをチェック
        heading_skip = False
        for i in range(len(headings_order) - 1):
            if headings_order[i+1] - headings_order[i] > 1:
                heading_skip = True
                break
        
        if not heading_skip and len(headings_order) > 0:
            score += 10
        elif heading_skip:
            issues.append("見出しレベルが飛ばされています（h2の後にh4など）")
        
        # リンクテキストのチェック
        links = self.soup.find_all('a')
        empty_links = [link for link in links if not link.get_text().strip() and not link.get('aria-label')]
        accessibility['empty_links_count'] = len(empty_links)
        
        if len(empty_links) == 0 and len(links) > 0:
            score += 10
        elif len(empty_links) > 0:
            issues.append(f"{len(empty_links)}個のリンクにテキストがありません")
        
        # タブインデックスの確認
        negative_tabindex = self.soup.find_all(attrs={'tabindex': lambda x: x and int(x) < 0})
        if len(negative_tabindex) > 0:
            issues.append(f"負のtabindex値が使用されています（{len(negative_tabindex)}個）")
        
        accessibility['score'] = min(score, 100)
        accessibility['issues'] = issues
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
        print(f"\n🎯 総合スコア: {self.results['overall_score']}/100")
    
    def generate_report(self):
        """診断レポートの生成"""
        report = []
        report.append("=" * 80)
        report.append(f"ウェブサイト診断レポート")
        report.append("=" * 80)
        report.append(f"URL: {self.url}")
        report.append(f"診断日時: {self.results['timestamp']}")
        report.append(f"総合スコア: {self.results['overall_score']}/100")
        report.append("=" * 80)
        report.append("")
        
        # 各カテゴリの詳細
        categories = [
            ('SEO診断', 'seo', '📊'),
            ('セキュリティ診断', 'security', '🔒'),
            ('パフォーマンス診断', 'performance', '⚡'),
            ('アクセシビリティ診断', 'accessibility', '♿')
        ]
        
        for title, key, icon in categories:
            data = self.results[key]
            report.append(f"\n{icon} {title}")
            report.append("-" * 80)
            report.append(f"スコア: {data['score']}/100")
            
            if data['issues']:
                report.append("\n【改善が必要な項目】")
                for issue in data['issues']:
                    report.append(f"  • {issue}")
            else:
                report.append("\n✅ 問題は見つかりませんでした")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """メイン関数"""
    print("=" * 80)
    print("🔍 ウェブサイト診断ツール")
    print("=" * 80)
    print("")
    
    # URLの入力
    url = input("診断するURLを入力してください: ").strip()
    
    if not url:
        print("❌ URLが入力されていません")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print("")
    
    # 診断の実行
    tool = WebsiteDiagnosisTool(url)
    results = tool.run_diagnosis()
    
    if results:
        print("\n" + "=" * 80)
        print(tool.generate_report())
        
        # 結果をJSONファイルに保存
        output_file = f"diagnosis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 詳細な診断結果を {output_file} に保存しました")


if __name__ == "__main__":
    main()
