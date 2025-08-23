# Transaction 1 — Mint (tx: `0x51d16a…2b338`)

Link: [https://hyperevmscan.io/tx/0x51d16ac2a407cbe0f852f44d7142a7deea8364026d726892e52990f384a2b338#eventlog](https://hyperevmscan.io/tx/0x51d16ac2a407cbe0f852f44d7142a7deea8364026d726892e52990f384a2b338#eventlog)

**Event A — `Mint`** (contract `0xf669ffe4b97e8c5603c52fcf157159e1120bfc72`)

* owner (topic): `0x6eDA206207c09e5428F281761DdC0D300851fBC8`
* tickLower (topic): `-2908`
* tickUpper (topic): `2201`
* sender: `0x6eDA206207c09e5428F281761DdC0D300851fBC8`
* amount (uint128 - liquidity): `474112528461144735`
* amount0 (uint256): `50000000000000000`
* amount1 (uint256): `63561641735124175`

**Event B — `IncreaseLiquidity`** (contract `0x6eda206207c09e5428f281761ddc0d300851fbc8` — HyperSwap V3: NFT Position Manager)

* tokenId (topic): `120570`
* liquidity (uint128): `474112528461144735`
* amount0 (uint256): `50000000000000000`
* amount1 (uint256): `63561641735124175`

---

# Transaction 2 — Add LP (tx: `0xb525ee…11e6`)

Link: [https://hyperevmscan.io/tx/0xb525ee945d6b6007214ea7089381565c8a21ea2a0048623bb33a7637606b11e6](https://hyperevmscan.io/tx/0xb525ee945d6b6007214ea7089381565c8a21ea2a0048623bb33a7637606b11e6)

**Event A — `Mint`** (contract `0xf669ffe4b97e8c5603c52fcf157159e1120bfc72`)

* owner (topic): `0x6eDA206207c09e5428F281761DdC0D300851fBC8`
* tickLower (topic): `-2908`
* tickUpper (topic): `2201`
* sender: `0x6eDA206207c09e5428F281761DdC0D300851fBC8`
* amount (uint128 - liquidity): `474112528461144735`
* amount0 (uint256): `50000000000000000`
* amount1 (uint256): `63561641735124175`

**Event B — `IncreaseLiquidity`** (contract `0x6eda206207c09e5428f281761ddc0d300851fbc8`)

* tokenId (topic): `120570`
* liquidity (uint128): `474112528461144735`
* amount0 (uint256): `50000000000000000`
* amount1 (uint256): `63561641735124175`

*(This tx shows the same Mint / IncreaseLiquidity details as the first — likely the same position/liquidity added under tokenId `120570`.)*

---

# Transaction 3 — Remove LP (tx: `0xd36f59…79d3c`)

Link: [https://hyperevmscan.io/tx/0xd36f592bf2753bfca8375d7c02e9b66a756a3fce8a04ebcd4fdf067be5179d3c](https://hyperevmscan.io/tx/0xd36f592bf2753bfca8375d7c02e9b66a756a3fce8a04ebcd4fdf067be5179d3c)

**Event A — `Burn`** (contract `0xf669ffe4b97e8c5603c52fcf157159e1120bfc72`)

* owner (topic): `0x6eDA206207c09e5428F281761DdC0D300851fBC8`
* tickLower (topic): `-2908`
* tickUpper (topic): `2201`
* amount (uint128 - liquidity): `237056264230572367`
* amount0 (uint256): `24999999999999999`
* amount1 (uint256): `31780820867562087`

**Event B — `DecreaseLiquidity`** (contract `0x6eda206207c09e5428f281761ddc0d300851fbc8`)

* tokenId (topic): `120570`
* liquidity (uint128): `237056264230572367`
* amount0 (uint256): `24999999999999999`
* amount1 (uint256): `31780820867562087`

**Event C — `Burn` (second entry)** (contract `0xf669ffe4b97e8c5603c52fcf157159e1120bfc72`)

* owner (topic): `0x6eDA206207c09e5428F281761DdC0D300851fBC8`
* tickLower (topic): `-2908`
* tickUpper (topic): `2201`
* amount: `0`
* amount0: `0`
* amount1: `0`

---
