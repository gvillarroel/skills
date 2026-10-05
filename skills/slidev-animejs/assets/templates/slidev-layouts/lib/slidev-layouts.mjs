// Copy with components/SlidevLayout.vue. No dependencies beyond native JavaScript.
const sequences = {
  colorset1: ['#9e1b32', '#000000', '#828282', '#1c1c1c', '#9c9c9c', '#363636', '#b5b5b5', '#333e48', '#cfcfcf', '#4f4f4f', '#e7e7e7', '#696969', '#f7f7f7', '#ffffff', '#6d1222', '#e8002a', '#ffccd5'],
  colorset2: ['#9e1b32', '#007298', '#e77204', '#45842a', '#652f6c', '#f1c319', '#6d1222', '#004d66', '#994a00', '#294d19', '#431f47', '#98700c', '#e8002a', '#00ace6', '#ff9633', '#36b300', '#9e00b3', '#ffd332', '#333e48', '#4f4f4f', '#696969', '#828282', '#9c9c9c', '#b5b5b5', '#1c1c1c', '#363636', '#000000', '#cfcfcf', '#e7e7e7', '#ffccd5', '#cdf3ff', '#dbffcc', '#f9ccff', '#ffe5cc', '#fff4cc', '#ffffff', '#f7f7f7'],
};
const modes = new Set(['columns', 'grid', 'masonry-columns', 'masonry-rows']);

function positive(value, name, integer = false) {
  if (!Number.isFinite(value) || value <= 0 || (integer && !Number.isInteger(value)))
    throw new RangeError(`${name} must be a positive ${integer ? 'integer' : 'number'}.`);
  return value;
}

export function layoutTheme(colorset = 'colorset1') {
  if (!sequences[colorset]) throw new RangeError(`Unknown colorset: ${colorset}.`);
  return Object.freeze({ colorset, canvas: '#ffffff', ink: '#000000', primary: '#9e1b32', quiet: '#e7e7e7', line: '#696969', font: '"Open Sans", Arial, sans-serif' });
}

export function relativeLuminance(hex) {
  if (!/^#[0-9a-f]{6}$/i.test(hex)) throw new TypeError('Colors must use six-digit hexadecimal notation.');
  const channels = [1, 3, 5].map(start => {
    const value = parseInt(hex.slice(start, start + 2), 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
}

export function textOnFill(fill) {
  const luminance = relativeLuminance(fill);
  return (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05) ? '#000000' : '#ffffff';
}

export function categoryId(item) {
  return String(item.category ?? item.id);
}

// Pass a previous order to append identities without reassigning existing paint.
export function extendCategoryOrder(order = [], items = []) {
  const result = order.map(String);
  if (new Set(result).size !== result.length) throw new TypeError('categoryOrder must contain unique identities.');
  const seen = new Set(result);
  for (const item of items) {
    const identity = categoryId(item);
    if (!seen.has(identity)) { seen.add(identity); result.push(identity); }
  }
  return result;
}

export function categoryPaints(items, { colorset = 'colorset1', categoryOrder = [], canvas = '#ffffff' } = {}) {
  layoutTheme(colorset);
  if (!sequences[colorset].includes(canvas.toLowerCase())) throw new RangeError('The canvas must belong to the selected exact palette.');
  const order = extendCategoryOrder(categoryOrder, items);
  const solids = sequences[colorset].filter(fill => fill !== canvas.toLowerCase());
  if (solids.length === 0) throw new RangeError('The canvas must leave usable category fills.');
  return new Map(order.map((identity, index) => {
    const fill = solids[index % solids.length];
    const overflowTier = Math.floor(index / solids.length);
    return [identity, Object.freeze({
      fill, ink: textOnFill(fill), categoryIndex: index, overflowTier,
      borderColor: textOnFill(fill),
      borderWidth: overflowTier === 0 ? 0 : 1 + ((overflowTier - 1) % 3),
      borderStyle: overflowTier === 0 ? 'solid' : ['solid', 'dashed', 'dotted'][Math.floor((overflowTier - 1) / 3) % 3],
    })];
  }));
}

/**
 * Plan native CSS-pixel geometry, preserving natural content sizes.
 * measurements maps item IDs to intrinsic {height, width}. Missing heights use
 * minItemHeight. rows is literal for grid/masonry-rows. page is one-based.
 */
export function planSlideLayout({
  items = [], mode = 'grid', columns = 3, rows = 3, width = 900, height = 390,
  gap = 16, minItemWidth = 140, minItemHeight = 96, page = 1, pageSize,
  measurements = {}, colorset = 'colorset1', categoryOrder = [],
} = {}) {
  if (!Array.isArray(items)) throw new TypeError('items must be an array.');
  if (!modes.has(mode)) throw new RangeError(`Unknown layout mode: ${mode}.`);
  for (const [name, value] of Object.entries({ columns, rows, page })) positive(value, name, true);
  for (const [name, value] of Object.entries({ width, height, minItemWidth, minItemHeight })) positive(value, name);
  if (!Number.isFinite(gap) || gap < 0) throw new RangeError('gap must be a nonnegative number.');
  const ids = items.map(item => {
    if (!item || typeof item.id !== 'string' || item.id.length === 0) throw new TypeError('Every item needs a nonempty string id.');
    return item.id;
  });
  if (new Set(ids).size !== ids.length) throw new TypeError('Item ids must be unique.');
  const countPerPage = pageSize === undefined ? Math.max(1, items.length) : positive(pageSize, 'pageSize', true);
  const pages = Math.max(1, Math.ceil(items.length / countPerPage));
  if (page > pages) throw new RangeError(`page must not exceed ${pages}.`);
  const start = (page - 1) * countPerPage;
  const selected = items.slice(start, start + countPerPage);
  for (const item of selected) {
    for (const [dimension, measured] of Object.entries(measurements[item.id] ?? {})) {
      if (dimension === 'height' || dimension === 'width') positive(measured, `measurements.${item.id}.${dimension}`);
    }
  }
  // Allocate from the complete input, never from the selected page.
  const paints = categoryPaints(items, { colorset, categoryOrder });
  const columnWidth = Math.max(minItemWidth, (width - gap * (columns - 1)) / columns);
  const naturalHeight = item => {
    const measured = measurements[item.id]?.height;
    if (measured !== undefined) positive(measured, `measurements.${item.id}.height`);
    return Math.max(minItemHeight, measured ?? minItemHeight);
  };
  const boxes = [];
  const put = (item, index, x, y, itemWidth, itemHeight, row, column) => {
    const paint = paints.get(categoryId(item));
    boxes.push({ item, index: start + index, id: item.id, category: categoryId(item),
      x, y, width: itemWidth, height: itemHeight, row, column,
      contentWidth: Math.max(1, itemWidth - 28 - 2 * paint.borderWidth),
      contentHeight: Math.max(1, itemHeight - 28 - 2 * paint.borderWidth), ...paint });
  };

  if (mode === 'grid') {
    const rowMinimum = Math.max(minItemHeight, (height - gap * (rows - 1)) / rows);
    const rowHeight = Math.max(rowMinimum, ...selected.map(naturalHeight));
    let y = 0;
    for (let offset = 0, row = 0; offset < selected.length; offset += columns, row++) {
      const group = selected.slice(offset, offset + columns);
      group.forEach((item, column) => put(item, offset + column, column * (columnWidth + gap), y, columnWidth, rowHeight, row, column));
      y += rowHeight + gap;
    }
  } else if (mode === 'columns') {
    let offset = 0;
    for (let column = 0; column < columns; column++) {
      const count = Math.floor(selected.length / columns) + (column < selected.length % columns ? 1 : 0);
      const cellMinimum = count === 0 ? minItemHeight : Math.max(minItemHeight, (height - gap * (count - 1)) / count);
      let y = 0;
      for (let row = 0; row < count; row++) {
        const item = selected[offset];
        const itemHeight = Math.max(cellMinimum, naturalHeight(item));
        put(item, offset, column * (columnWidth + gap), y, columnWidth, itemHeight, row, column);
        y += itemHeight + gap;
        offset++;
      }
    }
  } else if (mode === 'masonry-columns') {
    const ends = Array(columns).fill(0);
    const counts = Array(columns).fill(0);
    selected.forEach((item, index) => {
      const column = ends.indexOf(Math.min(...ends));
      const itemHeight = naturalHeight(item);
      put(item, index, column * (columnWidth + gap), ends[column], columnWidth, itemHeight, counts[column], column);
      ends[column] += itemHeight + gap;
      counts[column]++;
    });
  } else {
    const rowHeight = Math.max(minItemHeight, (height - gap * (rows - 1)) / rows, ...selected.map(naturalHeight));
    const ends = Array(rows).fill(0);
    const counts = Array(rows).fill(0);
    selected.forEach((item, index) => {
      const row = ends.indexOf(Math.min(...ends));
      const itemWidth = item.width === undefined ? minItemWidth : positive(item.width, `items.${item.id}.width`);
      put(item, index, ends[row], row * (rowHeight + gap), Math.max(minItemWidth, itemWidth), rowHeight, row, counts[row]);
      ends[row] += Math.max(minItemWidth, itemWidth) + gap;
      counts[row]++;
    });
  }

  const requiredWidth = Math.max(0, ...boxes.map(box => box.x + Math.max(box.width, measurements[box.id]?.width ?? 0)));
  const requiredHeight = Math.max(0, ...boxes.map(box => box.y + box.height));
  const reasons = [];
  if (requiredWidth > width + 0.5) reasons.push('frame-width');
  if (requiredHeight > height + 0.5) reasons.push('frame-height');
  if (boxes.some(box => (measurements[box.id]?.width ?? 0) > box.width + 0.5)) reasons.push('item-width');
  const overflowIds = boxes.filter(box => (measurements[box.id]?.width ?? 0) > box.width + 0.5 || box.x + Math.max(box.width, measurements[box.id]?.width ?? 0) > width + 0.5 || box.y + box.height > height + 0.5).map(box => box.id);
  return {
    mode, colorset, width, height, gap, items: boxes, fits: reasons.length === 0,
    requiredWidth, requiredHeight, reasons, overflowIds, page, pages,
    pageSize: countPerPage, totalItems: items.length, visibleIds: boxes.map(box => box.id),
    categoryOrder: [...paints.keys()], solidCapacity: sequences[colorset].length - 1,
    configuredRows: rows, configuredColumns: columns,
    occupiedRows: new Set(boxes.map(box => box.row)).size,
    occupiedColumns: new Set(boxes.map(box => box.column)).size,
  };
}
