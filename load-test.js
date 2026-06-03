import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const endpoints = [
    'http://localhost:5001/health',
    'http://localhost:5002/health',
    'http://localhost:5003/health',
  ];

  const url = endpoints[Math.floor(Math.random() * endpoints.length)];

  const res = http.get(url);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}