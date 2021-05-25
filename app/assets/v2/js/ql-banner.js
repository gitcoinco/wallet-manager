// set up the kinetics (using custom implementation to contain the particles in a single el)
const kinetics = new Kinetics({
  // to fill the full-size banner we need to take measurements from here
  container: document.querySelector('#ql-banner'),
  // but for z-indexing we need to append the canvas here
  prependTo: document.querySelector('#ql-banner-inner'),
  // we want the canvas to be absolutely positioned
  canvas: {
    handlePosition: false,
    style: {
      position: 'absolute',
      pointerEvents: 'none',
      zIndex: 1
    }
  },
  // ignore scroll methods
  unpausable: true,
  // configure the particles
  particles: {
    count: 32, size: {min: 100, max: 300}, rotate: {speed: 0.1},
    mode: {type: 'wind-from-right', boundery: 'endless', speed: '2' }
  }
}, document.querySelector('#ql-banner'));

// hook the particles
kinetics.interactionHook();

// targeted view
let target = 'lg';

// available sizes for the banner
const targets = {
  md: {
    heightDiff: 240,
    fontSizeLow: 1.5,
    fontSizeHigh: 3,
    paddingTopLow: 0,
    paddingTopHigh: 202
  },
  sm: {
    heightDiff: 440,
    fontSizeLow: 1.5,
    fontSizeHigh: 2,
    paddingTopLow: 0,
    paddingTopHigh: 404
  },
  xs: {
    heightDiff: 440,
    fontSizeLow: 1.1,
    fontSizeHigh: 2,
    paddingTopLow: 0,
    paddingTopHigh: 415
  }
};

// grab the elements
const banner = document.getElementById('ql-banner');
const bannerH1 = document.getElementById('ql-banner-h1');
const bannerBtn = document.getElementById('ql-banner-btn');
const bannerHero = document.getElementById('ql-banner-hero');
const bannerCoin = document.getElementById('ql-banner-coin');

// change opacity of the inner content on load
const bannerInnerRow = document.querySelector('#ql-banner-inner .row');

// spin the coin
const spinCoin = () => {
  bannerCoin.classList.remove('spin-3d');
  // trigger reflow
  void bannerCoin.offsetWidth;
  bannerCoin.classList.add('spin-3d');
};

// move between low and high based on percent travelled
const shrink = (low, high, percent) => low + ((high - low) * (Math.max(0, percent) / 100));

// scroll-to-shrink --- alter font-size/padding/maxWidth based on scrollY
const styleOnScroll = () => {
  // manually calulate the distance travelled (max of 240 px)
  const percent = (100 - (100 / targets[target].heightDiff * window.scrollY));

  // transition between the large and small banners using the % travelled to decide sizes
  bannerH1.style.fontSize = `${Math.max(shrink(targets[target].fontSizeLow, targets[target].fontSizeHigh, percent), targets[target].fontSizeLow)}rem`;
  bannerH1.style.paddingTop = `${Math.min(shrink(targets[target].paddingTopLow, targets[target].paddingTopHigh, 100 - percent), targets[target].paddingTopHigh)}px`;

  // this low and high is fixed because we can overide with css - we don't need to cover edge cases
  const width = `${Math.max(shrink(258, 540, percent), 258)}px`;

  // set to both so that fullsize is locked to 540 (only shrinking when moving to smaller banner size)
  bannerHero.style.maxWidth = width;
  bannerHero.style.minWidth = width;
};

// ensure that we only fire 100 times to gather the styleOnScroll percentages
const createIntersectionObserver = () => {
  // create a new intersectionObserver that will call styleOnScroll for 100 steps (as the header intersects)
  new IntersectionObserver((entries) => entries.forEach(() => {
    // no need to send the per because we will caluclate it manually to stay responsive (md/sm/xs)
    styleOnScroll();
  }), {
    // fire for 100 steps
    threshold: [...new Array(100)].map((_, k) => (k / 100))
  }).observe(banner);
};

// set-up the targets size based on window width
const setTarget = () => {
  // hard coding these so that we dont have to wait for DOMContentLoaded (and xs starts early)
  if (window.innerWidth >= 768) {
    target = 'md';
  } else if (window.innerWidth < 767 && window.innerWidth > 557) {
    target = 'sm';
  } else {
    target = 'xs';
  }
  // ensure these new sizes are reflected
  styleOnScroll();
};

// first load
setTarget();
styleOnScroll();

// wait a tick to display to avoid flashing the wrong position
setTimeout(() => {
  // fade in on load
  bannerInnerRow.style.opacity = 1;
  bannerInnerRow.style.paddingTop = 0;
  // spin on load
  spinCoin();
});

// spin on click
bannerCoin.addEventListener('click', spinCoin);

// watch for intersection on the sticky banner (calling styleOnScroll)
createIntersectionObserver();

// shrink on scroll and make sure the shrink target sizes are correct on resize
window.addEventListener('resize', RAFThrottle(setTarget), { passive: true });

