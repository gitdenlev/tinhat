// Static copy for the left-hand marketing panel of the Accept page.
export const ACCEPT_PANEL = {
  title: "You've received a<br/>confidential secret.",
  subtitle:
    'This link contains an end-to-end encrypted secret message.<br/>Decide whether to open and decrypt it before it expires.',
  features: [
    {
      icon: 'flame',
      title: 'Burn after reading',
      desc: 'Permanently wiped right after viewing or when the link expires.'
    },
    {
      icon: 'shield',
      title: 'End-to-end encrypted',
      desc: 'Decrypted only inside your browser. No server copies.'
    },
    {
      icon: 'ghost',
      title: 'Zero trace left behind',
      desc: 'No accounts, no history, no logs stored anywhere.'
    }
  ]
};

// Static copy for the left-hand panel of the Link Not Found / Expired page.
export const LINK_NOT_FOUND_PANEL = {
  title: 'Nothing is stored.<br/>Nothing can leak.',
  subtitle:
    'Tinhat is engineered without persistent storage. Once a secret is burned, recovery is impossible.',
  features: [
    {
      icon: 'shield',
      title: 'RAM-only architecture',
      desc: 'Secrets live strictly in volatile memory and never touch a hard disk or database.'
    },
    {
      icon: 'ghost',
      title: 'Zero tracking or logs',
      desc: 'No accounts, no IP logs, no personal data, and no digital footprints.'
    },
    {
      icon: 'clock',
      title: 'Strict lifetime control',
      desc: 'Every link has an expiration timer from 5 minutes to 24 hours.'
    }
  ]
};
