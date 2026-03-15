// eslint.config.mjs
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';

export default [
  {
    files: ['**/*.ts', '**/*.js'],

    languageOptions: {
      parser: tsparser,
      sourceType: 'module',
      parserOptions: {
        ecmaVersion: 2022
      }
    },

    plugins: {
      '@typescript-eslint': tseslint
    },

    rules: {
      ...tseslint.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': 'warn',
      '@typescript-eslint/no-require-imports': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-console': 'warn',
      semi: ['error', 'always'],
      quotes: ['error', 'single', { avoidEscape: true }]
    }
  },
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      'coverage/**',
      '*.config.js',
      '*.config.mjs'
    ]
  }
];
