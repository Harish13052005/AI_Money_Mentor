module.exports = ({ config }) => ({
  ...config,
  extra: {
    ...config.extra,
    API_BASE: "http://192.168.0.108:8000",
    eas: {
      projectId: "f4a0eed7-b052-4b34-bbde-66164234e67c"
    }
  }
});