/**
 * SellBuddy - Google Apps Script for Order Management
 *
 * SETUP INSTRUCTIONS:
 * 1. Create a new Google Sheet
 * 2. Go to Extensions > Apps Script
 * 3. Paste this entire code
 * 4. Click Deploy > New Deployment > Web App
 * 5. Set "Execute as: Me" and "Who has access: Anyone"
 * 6. Copy the Web App URL and add it to your environment as GOOGLE_SHEETS_WEBHOOK
 * 7. Create sheets named: "Orders", "Analytics", "Inventory", "Customers"
 */

// Configuration
const CONFIG = {
  ordersSheet: 'Orders',
  analyticsSheet: 'Analytics',
  inventorySheet: 'Inventory',
  customersSheet: 'Customers',
  ownerEmail: 'nazmulaminashiq.coder@gmail.com',
  storeName: 'SellBuddy'
};

/**
 * Handle incoming POST requests (webhooks)
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    // Determine the type of webhook
    if (data.order_id) {
      return handleNewOrder(data);
    } else if (data.analytics) {
      return handleAnalyticsUpdate(data);
    } else if (data.inventory_update) {
      return handleInventoryUpdate(data);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ success: true, message: 'Webhook received' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    console.error('Webhook error:', error);
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Handle GET requests (for testing)
 */
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'active',
      service: 'SellBuddy Order Webhook',
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Process new order
 */
function handleNewOrder(order) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. Add to Orders sheet
  const ordersSheet = ss.getSheetByName(CONFIG.ordersSheet) || createOrdersSheet(ss);

  ordersSheet.appendRow([
    order.order_id,
    order.date,
    order.customer_name,
    order.customer_email,
    order.phone || '',
    order.items,
    order.subtotal,
    order.shipping,
    order.tax,
    order.total,
    order.shipping_address,
    order.status,
    new Date().toISOString() // Received timestamp
  ]);

  // 2. Update/Add customer
  updateCustomer(ss, order);

  // 3. Update analytics
  updateDailyAnalytics(ss, order);

  // 4. Send notification email
  sendOrderNotification(order);

  // 5. Highlight high-value orders
  if (order.total >= 100) {
    highlightHighValueOrder(ordersSheet);
  }

  return ContentService
    .createTextOutput(JSON.stringify({
      success: true,
      order_id: order.order_id,
      message: 'Order processed successfully'
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Create Orders sheet with headers
 */
function createOrdersSheet(ss) {
  const sheet = ss.insertSheet(CONFIG.ordersSheet);

  // Set headers
  const headers = [
    'Order ID', 'Date', 'Customer Name', 'Email', 'Phone',
    'Items', 'Subtotal', 'Shipping', 'Tax', 'Total',
    'Shipping Address', 'Status', 'Received At'
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length)
    .setBackground('#4f46e5')
    .setFontColor('white')
    .setFontWeight('bold');

  // Set column widths
  sheet.setColumnWidth(1, 150); // Order ID
  sheet.setColumnWidth(2, 120); // Date
  sheet.setColumnWidth(3, 150); // Customer Name
  sheet.setColumnWidth(4, 200); // Email
  sheet.setColumnWidth(6, 300); // Items
  sheet.setColumnWidth(11, 250); // Address

  // Freeze header row
  sheet.setFrozenRows(1);

  return sheet;
}

/**
 * Update customer database
 */
function updateCustomer(ss, order) {
  const sheet = ss.getSheetByName(CONFIG.customersSheet) || createCustomersSheet(ss);
  const data = sheet.getDataRange().getValues();

  // Find existing customer
  let customerRow = -1;
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === order.customer_email) { // Email is in column B
      customerRow = i + 1;
      break;
    }
  }

  if (customerRow > 0) {
    // Update existing customer
    const currentOrders = sheet.getRange(customerRow, 4).getValue() || 0;
    const currentSpent = sheet.getRange(customerRow, 5).getValue() || 0;

    sheet.getRange(customerRow, 4).setValue(currentOrders + 1);
    sheet.getRange(customerRow, 5).setValue(currentSpent + order.total);
    sheet.getRange(customerRow, 6).setValue(new Date().toISOString());
  } else {
    // Add new customer
    sheet.appendRow([
      order.customer_name,
      order.customer_email,
      order.phone || '',
      1, // Order count
      order.total, // Total spent
      new Date().toISOString(), // Last order
      order.shipping_address
    ]);
  }
}

/**
 * Create Customers sheet
 */
function createCustomersSheet(ss) {
  const sheet = ss.insertSheet(CONFIG.customersSheet);

  const headers = ['Name', 'Email', 'Phone', 'Orders', 'Total Spent', 'Last Order', 'Address'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length)
    .setBackground('#10b981')
    .setFontColor('white')
    .setFontWeight('bold');

  sheet.setFrozenRows(1);
  return sheet;
}

/**
 * Update daily analytics
 */
function updateDailyAnalytics(ss, order) {
  const sheet = ss.getSheetByName(CONFIG.analyticsSheet) || createAnalyticsSheet(ss);
  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const data = sheet.getDataRange().getValues();

  // Find today's row
  let todayRow = -1;
  for (let i = 1; i < data.length; i++) {
    const rowDate = Utilities.formatDate(new Date(data[i][0]), Session.getScriptTimeZone(), 'yyyy-MM-dd');
    if (rowDate === today) {
      todayRow = i + 1;
      break;
    }
  }

  if (todayRow > 0) {
    // Update existing row
    const currentOrders = sheet.getRange(todayRow, 2).getValue() || 0;
    const currentRevenue = sheet.getRange(todayRow, 3).getValue() || 0;

    sheet.getRange(todayRow, 2).setValue(currentOrders + 1);
    sheet.getRange(todayRow, 3).setValue(currentRevenue + order.total);
  } else {
    // Add new row for today
    sheet.appendRow([
      new Date(),
      1,
      order.total,
      0, // Visitors (placeholder)
      0  // Conversion rate (placeholder)
    ]);
  }
}

/**
 * Create Analytics sheet
 */
function createAnalyticsSheet(ss) {
  const sheet = ss.insertSheet(CONFIG.analyticsSheet);

  const headers = ['Date', 'Orders', 'Revenue', 'Visitors', 'Conversion %'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length)
    .setBackground('#f59e0b')
    .setFontColor('white')
    .setFontWeight('bold');

  // Format revenue column as currency
  sheet.getRange('C:C').setNumberFormat('$#,##0.00');
  sheet.getRange('E:E').setNumberFormat('0.00%');

  sheet.setFrozenRows(1);
  return sheet;
}

/**
 * Handle inventory updates
 */
function handleInventoryUpdate(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.inventorySheet) || createInventorySheet(ss);

  // Process inventory update
  // This could be expanded based on your needs

  return ContentService
    .createTextOutput(JSON.stringify({ success: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Create Inventory sheet
 */
function createInventorySheet(ss) {
  const sheet = ss.insertSheet(CONFIG.inventorySheet);

  const headers = ['SKU', 'Product Name', 'Stock', 'Supplier', 'Cost', 'Price', 'Margin', 'Status'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length)
    .setBackground('#ef4444')
    .setFontColor('white')
    .setFontWeight('bold');

  sheet.setFrozenRows(1);
  return sheet;
}

/**
 * Handle analytics webhook updates
 */
function handleAnalyticsUpdate(data) {
  // Process analytics data from the bots
  return ContentService
    .createTextOutput(JSON.stringify({ success: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Send order notification email
 */
function sendOrderNotification(order) {
  const subject = `[${CONFIG.storeName}] New Order #${order.order_id} - $${order.total}`;

  const body = `
NEW ORDER RECEIVED!

Order ID: ${order.order_id}
Date: ${order.date}

Customer: ${order.customer_name}
Email: ${order.customer_email}
Phone: ${order.phone || 'Not provided'}

Items: ${order.items}

Total: $${order.total}

Shipping Address:
${order.shipping_address}

---
View all orders in your Google Sheet.
  `;

  try {
    MailApp.sendEmail(CONFIG.ownerEmail, subject, body);
  } catch (e) {
    console.error('Email error:', e);
  }
}

/**
 * Highlight high-value orders
 */
function highlightHighValueOrder(sheet) {
  const lastRow = sheet.getLastRow();
  sheet.getRange(lastRow, 1, 1, sheet.getLastColumn())
    .setBackground('#fef3c7'); // Light yellow background
}

/**
 * Daily summary trigger - set this up in Triggers
 */
function sendDailySummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ordersSheet = ss.getSheetByName(CONFIG.ordersSheet);
  const analyticsSheet = ss.getSheetByName(CONFIG.analyticsSheet);

  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');

  // Get today's stats from analytics
  const analyticsData = analyticsSheet.getDataRange().getValues();
  let todayOrders = 0;
  let todayRevenue = 0;

  for (let i = 1; i < analyticsData.length; i++) {
    const rowDate = Utilities.formatDate(new Date(analyticsData[i][0]), Session.getScriptTimeZone(), 'yyyy-MM-dd');
    if (rowDate === today) {
      todayOrders = analyticsData[i][1];
      todayRevenue = analyticsData[i][2];
      break;
    }
  }

  const subject = `[${CONFIG.storeName}] Daily Summary - ${today}`;
  const body = `
DAILY SUMMARY FOR ${today}

Orders Today: ${todayOrders}
Revenue Today: $${todayRevenue.toFixed(2)}

---
View full details in your Google Sheet.
  `;

  MailApp.sendEmail(CONFIG.ownerEmail, subject, body);
}

/**
 * Weekly report trigger
 */
function sendWeeklyReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const analyticsSheet = ss.getSheetByName(CONFIG.analyticsSheet);
  const customersSheet = ss.getSheetByName(CONFIG.customersSheet);

  const data = analyticsSheet.getDataRange().getValues();
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

  let weeklyOrders = 0;
  let weeklyRevenue = 0;

  for (let i = 1; i < data.length; i++) {
    if (new Date(data[i][0]) >= oneWeekAgo) {
      weeklyOrders += data[i][1] || 0;
      weeklyRevenue += data[i][2] || 0;
    }
  }

  const totalCustomers = customersSheet ? customersSheet.getLastRow() - 1 : 0;

  const subject = `[${CONFIG.storeName}] Weekly Report`;
  const body = `
WEEKLY PERFORMANCE REPORT

Orders This Week: ${weeklyOrders}
Revenue This Week: $${weeklyRevenue.toFixed(2)}
Total Customers: ${totalCustomers}

Average Order Value: $${weeklyOrders > 0 ? (weeklyRevenue / weeklyOrders).toFixed(2) : '0.00'}

---
Keep up the great work!
  `;

  MailApp.sendEmail(CONFIG.ownerEmail, subject, body);
}

/**
 * Initialize the spreadsheet with all required sheets
 */
function initializeSpreadsheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  createOrdersSheet(ss);
  createCustomersSheet(ss);
  createAnalyticsSheet(ss);
  createInventorySheet(ss);

  // Set up triggers
  ScriptApp.newTrigger('sendDailySummary')
    .timeBased()
    .everyDays(1)
    .atHour(20) // 8 PM
    .create();

  ScriptApp.newTrigger('sendWeeklyReport')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.SUNDAY)
    .atHour(10) // 10 AM
    .create();

  Logger.log('Spreadsheet initialized successfully!');
}
