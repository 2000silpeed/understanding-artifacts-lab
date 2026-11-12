export function upperBound(keys, value) {
  let lo = 0;
  let hi = keys.length;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (keys[mid] <= value) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function leafNode() {
  return { keys: [], children: null, next: null, name: '' };
}

function innerNode() {
  return { keys: [], children: [], next: null, name: '' };
}

function insertAt(node, key, maxKeys) {
  if (node.children === null) {
    const at = upperBound(node.keys, key);
    if (at > 0 && node.keys[at - 1] === key) return { duplicate: true, split: null };
    node.keys.splice(at, 0, key);
    if (node.keys.length <= maxKeys) return { duplicate: false, split: null };
    const mid = Math.floor(node.keys.length / 2);
    const right = leafNode();
    right.keys = node.keys.slice(mid);
    node.keys = node.keys.slice(0, mid);
    right.next = node.next;
    node.next = right;
    return { duplicate: false, split: { separator: right.keys[0], right } };
  }

  const childIndex = upperBound(node.keys, key);
  const result = insertAt(node.children[childIndex], key, maxKeys);
  if (result.duplicate || result.split === null) return result;
  node.keys.splice(childIndex, 0, result.split.separator);
  node.children.splice(childIndex + 1, 0, result.split.right);
  if (node.keys.length <= maxKeys) return { duplicate: false, split: null };
  const mid = Math.floor(node.keys.length / 2);
  const separator = node.keys[mid];
  const right = innerNode();
  right.keys = node.keys.slice(mid + 1);
  right.children = node.children.slice(mid + 1);
  node.keys = node.keys.slice(0, mid);
  node.children = node.children.slice(0, mid + 1);
  return { duplicate: false, split: { separator, right } };
}

export function buildTree(keys, maxKeys = 3) {
  if (!Number.isInteger(maxKeys) || maxKeys < 3) throw new Error('max_keys must be at least 3');
  const tree = { maxKeys, root: leafNode() };
  for (const key of keys) {
    const result = insertAt(tree.root, key, maxKeys);
    if (result.duplicate) continue;
    if (result.split) {
      const root = innerNode();
      root.keys = [result.split.separator];
      root.children = [tree.root, result.split.right];
      tree.root = root;
    }
  }
  assignNames(tree);
  return tree;
}

export function assignNames(tree) {
  const levels = [];
  let level = [tree.root];
  while (level.length) {
    levels.push(level);
    level = level.flatMap((node) => node.children === null ? [] : node.children);
  }
  let inner = 0;
  levels.forEach((nodes, depth) => nodes.forEach((node, index) => {
    if (depth === 0) node.name = 'R';
    else if (node.children === null) node.name = `L${index + 1}`;
    else node.name = `I${++inner}`;
  }));
  return levels;
}

export function levels(tree) {
  return assignNames(tree);
}

export function leafChain(tree) {
  let node = tree.root;
  while (node.children !== null) node = node.children[0];
  const chain = [];
  while (node !== null) {
    chain.push(node);
    node = node.next;
  }
  return chain;
}

export function rangeCount(tree, lo, hi) {
  let node = tree.root;
  while (node.children !== null) node = node.children[upperBound(node.keys, lo)];
  let count = 0;
  let leavesRead = 0;
  while (node !== null) {
    leavesRead += 1;
    for (const key of node.keys) {
      if (key > hi) return { count, leavesRead };
      if (key >= lo) count += 1;
    }
    node = node.next;
  }
  return { count, leavesRead };
}

export function rangeSearch(tree, lo, hi) {
  let node = tree.root;
  const descent = [];
  while (node.children !== null) {
    descent.push(node.name);
    node = node.children[upperBound(node.keys, lo)];
  }
  const found = [];
  const walked = [];
  let stopKey = null;
  while (node !== null) {
    walked.push(node.name);
    for (const key of node.keys) {
      if (key > hi) {
        stopKey = key;
        return { found, descent, walked, stopKey, moves: descent.length + walked.length - 1 };
      }
      if (key >= lo) found.push(key);
    }
    node = node.next;
  }
  return { found, descent, walked, stopKey, moves: descent.length + walked.length - 1 };
}

export function noLinkRangeSearch(tree, lo, hi) {
  const route = [];
  const stack = [];
  let node = tree.root;
  while (node.children !== null) {
    route.push(node.name);
    const index = upperBound(node.keys, lo);
    stack.push([node, index]);
    node = node.children[index];
  }
  const found = [];
  while (true) {
    route.push(node.name);
    for (const key of node.keys) {
      if (key > hi) return { found, route, moves: route.length - 1 };
      if (key >= lo) found.push(key);
    }
    while (stack.length && stack.at(-1)[1] === stack.at(-1)[0].children.length - 1) {
      route.push(stack.pop()[0].name);
    }
    if (!stack.length) return { found, route, moves: route.length - 1 };
    const parent = stack.at(-1);
    route.push(parent[0].name);
    parent[1] += 1;
    node = parent[0].children[parent[1]];
    while (node.children !== null) {
      route.push(node.name);
      stack.push([node, 0]);
      node = node.children[0];
    }
  }
}

export const CANONICAL = Object.freeze({
  maxKeys: 3,
  insertOrder: Object.freeze([12, 31, 8, 45, 19, 27, 52, 15, 36, 21, 41, 24, 33, 30]),
  sortedKeys: Object.freeze([8, 12, 15, 19, 21, 24, 27, 30, 31, 33, 36, 41, 45, 52]),
  expectedLevels: Object.freeze([
    Object.freeze(['R[31]']),
    Object.freeze(['I1[19,24]', 'I2[36,45]']),
    Object.freeze(['L1[8,12,15]', 'L2[19,21]', 'L3[24,27,30]', 'L4[31,33]', 'L5[36,41]', 'L6[45,52]']),
  ]),
});
