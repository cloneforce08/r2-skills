// Bad test file that needs improvement
// Issues: no imports from 'vitest', no describe blocks, no AAA pattern,
// descriptions in English, testing private members, mixed unrelated tests

test('truncate works', () => {
  const result = truncate('hello world', 5);
  expect(result).toBe('he...');
});

test('slugify test', () => {
  expect(slugify('Hello World!')).toBe('hello-world');
});

test('cart add item', () => {
  const cart = new CartService();
  cart.add({ id: '1', name: 'Product', price: 10, quantity: 1 });
  expect(cart['items'].length).toBe(1); // accessing private member!
});

test('cart total with no discount', () => {
  const cart = new CartService();
  cart.add({ id: '1', name: 'Product', price: 10, quantity: 2 });
  const total = cart.getTotal();
  expect(total).toBe(20);
});

test('capitalize first letter', () => {
  expect(capitalize('hello')).toBe('Hello');
});

test('cart remove', () => {
  const cart = new CartService();
  cart.add({ id: '1', name: 'Product', price: 10, quantity: 1 });
  cart.remove('1');
  expect(cart.getItems()).toHaveLength(0);
});
