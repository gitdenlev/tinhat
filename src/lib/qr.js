import QRCode from 'qrcode';

export async function generateQrSvg(url) {
  if (!url) return '';
  try {
    return await QRCode.toString(url, {
      type: 'svg',
      margin: 1,
      errorCorrectionLevel: 'M',
      color: { dark: '#0d0f1a', light: '#ffffff' }
    });
  } catch (err) {
    console.error('Failed to generate QR code:', err);
    return '';
  }
}
