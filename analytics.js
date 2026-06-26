// Google Analytics 4 + affiliate click tracking
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-Z0N6LDFJV5', { send_page_view: true });

document.addEventListener('click', function (event) {
  const link = event.target.closest('a[href]');
  if (!link || typeof gtag !== 'function') return;
  const url = link.href;
  const text = (link.innerText || link.getAttribute('aria-label') || '').trim().slice(0, 120);
  if (url.includes('x.com/gadget_tengoku') || url.includes('github.com/gadget-tengoku/gadget-lab/issues')) {
    gtag('event', 'contact_link_click', {
      contact_channel: url.includes('x.com') ? 'X' : 'GitHub Issues',
      link_url: url,
      page_path: location.pathname,
      transport_type: 'beacon'
    });
  } else if (url.includes('hb.afl.rakuten.co.jp')) {
    gtag('event', 'rakuten_affiliate_click', {
      affiliate_network: 'Rakuten',
      link_url: url,
      link_text: text,
      page_path: location.pathname,
      transport_type: 'beacon'
    });
  } else if (link.hostname && link.hostname !== location.hostname) {
    gtag('event', 'outbound_click', {
      link_domain: link.hostname,
      link_url: url,
      link_text: text,
      page_path: location.pathname,
      transport_type: 'beacon'
    });
  }
});
