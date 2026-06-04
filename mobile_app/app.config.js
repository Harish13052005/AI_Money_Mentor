module.exports = ({ config }) => ({
  ...config,
  extra: {
    API_BASE: process.env.API_BASE || ''
  }
});